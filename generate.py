from PIL import Image, ImageColor
# import numpy as np
from numpy import asarray
from tkinter import filedialog
import json
import math
from itertools import chain
# from datetime import date
# import time
# from datetime import time
from datetime import datetime

from shared import consistxels_version



def generate_all(input_data, output_folder_path, progress_callback = None): #input_data is already in proper structure for consistxels .json
    output_folder_path += "/"

    start_time = datetime.now()

    def update_progress(new_value = None, progress_text = None):
        if progress_callback != None:
            progress_callback(new_value, progress_text)

    update_progress(0, "Initializing...") # is Initializing the right word here?

    header = input_data["header"]
    search_data = input_data["search_data"]
    search_type_data = input_data["search_type_data"]
    generation_data = input_data["generation_data"]
    
    input_layer_data = input_data["layer_data"]
    input_pose_data = input_data["pose_data"]

    # search_types = ["Border", "Spacing", "Preset"]

    # output_pose_data = []

    match search_type_data["search_type"]:
        case "Border":
            pose_locations = search_border(search_data, search_type_data, input_layer_data, update_progress)
            # print(pose_locations)
        case "Spacing":
            # A bit clumsy, but it *should* work
            # Shouldn't NEED error detection, but might be good to put something here. i.e. if no layers w/ images are found. but might be better to put that above, in which case finding the img size can probably also move up
            layer = next(layer for layer in input_layer_data if (layer.get("search_image_path") or layer.get("source_image_path")))
            with Image.open(layer["search_image_path"] if layer.get("search_image_path") else layer["source_image_path"]) as img:
                size = img.size

            pose_locations = search_spacing(search_data, search_type_data, size, update_progress)
        case "Preset":
            pose_locations = input_pose_data # change to just be position/size?
        case _:
            pass # throw exception: invalid search type

    output_pose_data, image_prep_data = generate_pose_data(pose_locations, input_layer_data, search_data, generation_data, update_progress)
    # return
    image_data, images = generate_image_data(image_prep_data, input_layer_data, output_pose_data, update_progress)
    # images = generate_images(image_prep_data, input_layer_data, update_progress)

    update_progress(25, "Wrapping up; saving images...")
    
    # may want to think of better way to do this
    for i in range(len(image_data)):
        images[i].save(output_folder_path + image_data[i]["path"])

    update_progress(50, "Wrapping up; formatting layer data...")

    # save OUTPUT layer data, if appropriate checkboxes checked
    output_layer_data = generate_layer_data(input_layer_data, output_folder_path, header["paths_are_local"])
    # for layer in input_layer_data:
    #     search_image_path = None
    #     source_image_path = None

    #     if layer["export_original_images"]:
    #         # search_image_path = output_folder_path "{layer["name"]}_search_image" if header["paths_are_local"] and layer["search_image_path"] else None
    #         # source_image_path = output_folder_path "/""{layer["name"]}_search_image" if header["paths_are_local"] and layer["search_image_path"] else None

    #         if layer["search_image_path"]:
    #             search_image_path = ((output_folder_path if not header["paths_are_local"] else "")
    #                 + (f"{layer["name"]}_search_image.png" if not layer["is_border"] else "border.png"))

    #             with Image.open(layer["search_image_path"]) as search_image:
    #                 # search_image.save(((output_folder_path + "/") if not header["paths_are_local"] else "") + f"{layer["name"]}_search_image")
    #                 search_image.save(search_image_path)
    #         if layer["source_image_path"]:
    #             source_image_path = (output_folder_path if not header["paths_are_local"] else "") + f"{layer["name"]}_source_image.png"

    #             with Image.open(layer["source_image_path"]) as source_image:
    #                 source_image.save(((output_folder_path + "/") if not header["paths_are_local"] else "") + f"{layer["name"]}_source_image")

    #     output_layer_data.append({
    #         "name": layer["name"], "is_border": layer["is_border"], "is_cosmetic_only": layer["is_cosmetic_only"],
    #         "search_image_path": search_image_path,
    #         # "search_image_path": ((output_folder_path + "/") if not header["paths_are_local"] else "") + f"{layer["name"]}_search_image" if header["paths_are_local"] and layer["export_original_images"] and layer["search_image_path"] else None,
    #         "search_image_path": source_image_path
    #         # "search_image_path": ((output_folder_path + "/") if not header["paths_are_local"] else "") + f"{layer["name"]}_search_image" if header["paths_are_local"] and layer["export_original_images"] and layer["search_image_path"] else None
    #     })

    update_progress(75, "Wrapping up; saving output to .json...")

    output_data = {
        "header": header,
        "search_data": search_data,
        "search_type_data": search_type_data,
        "generation_data": generation_data,
        "layer_data": output_layer_data,
        "pose_data": output_pose_data,
        "image_data": image_data
    }

    json_filename = "consistxels_pose_output_" + header["name"] + ".json"

    with open(output_folder_path + json_filename, 'w') as file:
        json.dump(output_data, file, indent=4)    

    end_time = datetime.now()
    time_elapsed = end_time - start_time
    time_elapsed_seconds = int(time_elapsed.total_seconds())
    hours = time_elapsed_seconds // 3600
    minutes = (time_elapsed_seconds % 3600) // 60
    seconds = time_elapsed_seconds % 60
    formatted_time_elapsed = f"{hours:02}:{minutes:02}:{seconds:02}"
    # messagebox to alert user
    update_progress(100, f"Complete! Time elapsed: {formatted_time_elapsed}") # add time to this

def search_border(search_data, search_type_data, layer_data, update_progress):
    # Determine which layer is the border
    border_layer = next(layer for layer in layer_data if layer.get("is_border"))
    # throw exception if border_layer == None

    # Open the border image
    with Image.open(border_layer["search_image_path"]) as border_image:
        # Get image size
        # height, width = border_image.size()
        width, height = border_image.size
        # print(width, height)
        # width = border_image.size()[0]
        # height = border_image.size()[1]

        # Update progress, setup progress-related variable
        curr_percent = 0
        update_progress(0, f"Searching border image for valid pose boxes... (Pose boxes found: 0)")

        # Get color that will be treated as border edge (formatted for Image library, and made opaque)
        # TODO: test if values that already have alpha can make it here, and stop 'em. probably throw error too
        border_color_rgb = ImageColor.getrgb(search_type_data["border_color"] + "ff")

        # errors if these don't exist, I guess??
        start_search_in_center = search_data["start_search_in_center"]
        search_right_to_left = search_data["search_right_to_left"]

        pose_locations = []

        # always subtracting 2 from the ranges, because there is no pose that can fit in a 2-wide or 2-high box, inclusive of border - there's no space
        for y in range(height - 2): # rows
            for x in (get_x_range(0, width, start_search_in_center, search_right_to_left, -2)): # columns (subtracting 2 from right edge, as mentioned above)

                pixel = border_image.getpixel([x,y]) # get the pixel at the current coordinates

                # coordinates will be set to bottom-right corner of pose box
                endborder_x = -1
                endborder_y = -1

                if pixel == border_color_rgb: # i.e. if the current pixel is part of a pose box border:

                    # if the current pixel is in the shape of a top-left corner
                    # (works regardless of whether searching right-to-left or left-to-right)
                    if border_image.getpixel([x + 1, y]) == border_color_rgb \
                    and border_image.getpixel([x, y + 1]) == border_color_rgb \
                    and not border_image.getpixel([x + 1, y + 1]) == border_color_rgb:
                        
                        for x2 in range(x + 1, width): # iterate all the way to the right. if no border is found, it's not a pose box after all.
                            if border_image.getpixel([x2, y + 1]) == border_color_rgb:

                                endborder_x = x2 # set x position of bottom-right corner
                                break # no need to keep looking
                        
                        if endborder_x != -1: # if a border has been found, it's likely a pose box.
                            
                            for y2 in range(y + 1, height): # look for the bottom right of the pose box.
                                
                                pixel2 = border_image.getpixel([endborder_x, y2]) # pixel with which to find bottom-right of pose box

                                if pixel2 != border_color_rgb: break # if a non-border pixel's ever found, it's not a pose box.
                                
                                # if the current pixel2 is in the shape of a bottom-right corner
                                if border_image.getpixel([endborder_x - 1, y2]) == border_color_rgb \
                                and border_image.getpixel([endborder_x, y2 - 1]) == border_color_rgb \
                                and not border_image.getpixel([endborder_x - 1, y2 - 1]) == border_color_rgb: #pose box found!

                                    endborder_y = y2 # set y position of bottom-right corner
                                    break # no need to keep looking
            
                    # i.e. if there's a valid bottom-right corner (which guarantees, for our purposes, that there really is a pose box)
                    if endborder_x >= 0 and endborder_y >= 0:

                        # x and y coordinate are moved right and down 1, so that they're INSIDE the pose box, rather than on its border
                        found_pose_x = x + 1
                        found_pose_y = y + 1
                        found_pose_width = endborder_x - x# - 1
                        found_pose_height = endborder_y - y# - 1

                        # Pose location appended as object, to fit with formatting of other search types (preset specifically)
                        pose_locations.append({
                            "x_position": found_pose_x,
                            "y_position": found_pose_y,
                            "width": found_pose_width,
                            "height": found_pose_height,
                        })

                        # Update progress text
                        update_progress(None, f"Searching border image for valid pose boxes... (Pose boxes found: {len(pose_locations)})")
            
            # For updating progress bar
            # Not running for some reason???
            new_percent = math.floor((y / (height - 2)) * 100)
            if new_percent > curr_percent:
                curr_percent = new_percent
                update_progress(new_percent)
                # print("gothere")
    
    update_progress(100, f"Border search complete! (Pose boxes found: {len(pose_locations)})")

    # List of pose objects is returned
    return pose_locations

def search_spacing(search_data, search_type_data, size, update_progress):
    # Prepare variables
    rows = search_type_data["spacing_rows"]
    columns = search_type_data["spacing_columns"]
    total_poses = rows * columns # For showing progress
    
    update_progress(0, f"Preparing pose locations... (0/{total_poses})") # Update progress

    outer_padding = search_type_data["spacing_outer_padding"]
    inner_padding = search_type_data["spacing_inner_padding"]
    x_separation = search_type_data["spacing_x_separation"]
    y_separation = search_type_data["spacing_y_separation"]

    # errors if these don't exist, I guess??
    start_search_in_center = search_data["start_search_in_center"]
    search_right_to_left = search_data["search_right_to_left"]

    width, height = size

    # true_width = (width - (outer_padding * 2) - ((inner_padding * 2) * columns) - (x_separation * (columns - 1))) / columns

    sprite_width = math.floor((width - (outer_padding * 2) - ((inner_padding * 2) * columns) - (x_separation * (columns - 1))) / columns)
    sprite_height = math.floor((height - (outer_padding * 2) - ((inner_padding * 2) * rows) - (y_separation * (rows - 1))) / rows)

    pose_locations = []

    # Calculating the poses' positions based on the data provided
    for grid_y in rows:
        for grid_x in get_x_range(0, columns, start_search_in_center, search_right_to_left, 0):
            # Essentially, we're trying to find the top-left corner of every pose box.
            # Outer padding applies exactly once to all top-left corners of pose boxes, no matter what
            # Inner padding applies twice per pose box, but only applies once for the pose that's being looked at (it hasn't gone past the inner padding yet)
            # Sprite height/width and x/y separation apply only for sprites that have already been counted
            pose_locations.append({
                "x_position": outer_padding + ((inner_padding + sprite_width + x_separation) * grid_x) + ((inner_padding * (grid_x - 1)) if grid_x > 0 else 0),
                "y_position": outer_padding + ((inner_padding + sprite_height + y_separation) * grid_y) + ((inner_padding * (grid_y - 1)) if grid_y > 0 else 0),
                "width": sprite_width, "height": sprite_height
            })
            
            update_progress(math.floor((len(pose_locations) / total_poses) * 100), f"Preparing pose locations... ({len(pose_locations)}/{total_poses})")
    
    update_progress(100, f"Pose locations prepared! ({len(pose_locations)}/{len(pose_locations)})")
    return pose_locations

def generate_pose_data(pose_locations, layer_data, search_data, generation_data, update_progress):
    update_progress(0, "Unique images found: 0")

    # for storing unique images!
    # images = []
    # images = []
    # image_data = []
    
    # stores image padding. index matches images[]
    # format: [(left_padding, top_padding, right_padding, bottom_padding)]
    image_prep_data = []

    # opening layer images here so that we don't have to re-open and -close them over and over 
    layer_search_images = []
    # layer_source_images = [] # do we even NEED source images at this stage?

    for layer in layer_data:
        # I think there's probably a more efficient way to do this, but I don't wanna

        # If there's a search image, add it. If not, add None just to keep indexes correct
        if layer.get("search_image_path"):
            layer_search_images.append(Image.open(layer["search_image_path"]))
        else:
            layer_search_images.append(None)

        # Same as above
        # if layer.get("layer_source_image"):
        #     layer_source_images.append(Image.open(layer["layer_source_image"]))
        # else:
        #     layer_source_images.append(None)
    
    pose_data = []

    # Search through already-discovered poses
    for pose_index, pose_location in enumerate(pose_locations):
        # if pose_index > 100: return
        # crop parameter tuple: (left, top, right, bottom)
        pose_box = (
            pose_location["x_position"],
            pose_location["y_position"],
            pose_location["x_position"] + pose_location["width"] - 1,
            pose_location["y_position"] + pose_location["height"] - 1
        )
        # print(pose_box)
        # KEEP AN EYE ON THIS! did some different math this time, hopefully the different search methods line up just fine

        # TODO: comment
        limb_data = []

        # Search through every layer for sprites
        # TODO: At some point, make this part its own function
        for layer_index, layer in enumerate(layer_data):
            if pose_index == 41:
                print(f"{layer_index} got inside loop")

            if layer != None and layer_search_images[layer_index] != None and not layer["is_border"] and not layer["is_cosmetic_only"]:

                # we already opened the layer images provided, so that we don't have to open and close them every time we find a pose box
                curr_layer_image = layer_search_images[layer_index]
                curr_layer_name = layer["name"]

                # print(curr_layer_name)
                if pose_index == 41:
                    print(f"{layer_index} ({curr_layer_name}) got past layer existence if")

                unbound_image = curr_layer_image.crop(pose_box) # the full image inside the pose box

                # the rectangle inside the image that actually contains a sprite - everything else is just transparent pixels
                bbox = unbound_image.getbbox()
                        
                # getbbox() returns None if there's no sprite, so this is verifying that there's even a sprite in the first place
                if bbox:
                    if pose_index == 41:
                        print(f"{layer_index} ({curr_layer_name}) got past bbox if")

                    # (probably delete this comment)
                    # store info implied by bounding box - i.e. offset. this is for formatting purposes in export, BUT ALSO for deciding maximum bounds for each limb

                    # crop image down to bounding box, so that it can be compared to other stored images
                    bound_image = unbound_image.crop(bbox)

                    # if pose_index == 100: bound_image.show()

                    # if pose_index == 20: bound_image.show()
                            
                    # loop control
                    is_unique = True
                    # image_index = 0

                    # info for posed limbs, declared outside the loop so that they persist, but i dunno if python works like that
                    is_flipped = False # whether the image is flipped horizontally
                    # flip_v = False # whether the image is flipped vertically
                    rotation_amount = 0 # increment by 1, each represents 90 degrees

                    image_index = 0 # MAYBE this will make it persist?

                    if (search_data["detect_identical_images"] or search_data["detect_rotated_images"] or
                        search_data["detect_flip_v_images"] or search_data["detect_flip_v_images"]):
                        # check against stored images - check w/ flip_h, flip_y, & rotate. so like 12 checks per limb :(
                        # for i in range(len(image_prep_data)): # maybe we DONT want this to have image_index as the index? it controls some loop control earlier
                        for i, image_prep in enumerate(image_prep_data): # maybe we DONT want this to have image_index as the index? it controls some loop control earlier
                            # I would RATHER store the images, as I was doing before, but this is FINE...
                            # compare_to = curr_layer_image.crop((pose_box[0], pose_box[1], pose_box[2], pose_box[3])) # HOPEFULLY this math is good???
                            compare_to = layer_search_images[image_prep["original_layer_index"]].crop((
                                image_prep["original_pose_location"]["x_position"],
                                image_prep["original_pose_location"]["y_position"],
                                image_prep["original_pose_location"]["width"] + image_prep["original_pose_location"]["x_position"] - 1,
                                image_prep["original_pose_location"]["height"] + image_prep["original_pose_location"]["y_position"] - 1
                            )) # HOPEFULLY this math is good???
                            compare_to = compare_to.crop(compare_to.getbbox())

                            is_unique, is_flipped, rotation_amount = compare_images(
                                bound_image, compare_to,
                                search_data["detect_identical_images"], search_data["detect_rotated_images"],
                                search_data["detect_flip_h_images"], search_data["detect_flip_v_images"]
                            )

                            # if pose_index == 20: compare_to.show()


                            image_index = i
                            if not is_unique:
                                # if pose_index == 41 and curr_layer_name == "farleg":
                                #     compare_to.show()
                                break

                    if pose_index == 41:
                        print(f"{layer_index} ({curr_layer_name}) got past compare_images")
                    
                    # now, HOPEFULLY, image_index is still hangin' around. # UPDATE: it wasn't :(             

                    # padding is saved for a few reasons. mostly, it's there to make the sprites easier to edit in a separate program once
                    # they've been output. without the padding, there'd be no room to work with, and you'd need to increase the size of the sprites,
                    # and then everything would get cut off, and it'd just be a whole mess. minimum padding was chosen because it shows exactly
                    # where the padding can be such that nothing gets cut off, in any of the poses where the identical image is used. however,
                    # maximum padding, wherein one can choose to see maximum space available for even a single pose, even if it gets cut off,
                    # will also be available. as will custom padding values!!! so that's fun. TODO: make comment better
                    
                    left_padding = top_padding = right_padding = bottom_padding = generation_data["custom_padding_amount"]


                    # This padding stuff can't be moved to be later, since it still has to apply to `if is_unique`
                    if generation_data["automatic_padding_type"] != "None": # does string comparison work like this in Python?
                        left_padding += bbox[0]
                        top_padding += bbox[1]
                        right_padding += unbound_image.width - bbox[2]
                        bottom_padding += unbound_image.height - bbox[3]

                        # won't work cause what if negative custom padding AND auto type == "None"
                        # left_padding = max(0, left_padding + bbox[0])
                        # top_padding = max(0, top_padding + bbox[1])
                        # right_padding = max(0, right_padding + unbound_image.width - bbox[2])
                        # bottom_padding = max(0, bottom_padding + unbound_image.height - bbox[3])

                    left_padding = max(0, left_padding)
                    top_padding = max(0, top_padding)
                    right_padding = max(0, right_padding)
                    bottom_padding = max(0, bottom_padding)

                    # left_padding, top_padding, right_padding, bottom_padding = bbox

                    
                    if pose_index == 41:
                        print(f"{layer_index} ({curr_layer_name}) got up to is_unique if ({is_unique})")

                    if is_unique:
                        # print(image_index)

                        # image_data.append({
                        #     "path": "",
                        #     "original_pose_index": pose_index # TODO: THIS CAUSES MAJOR ISSUES!!! Basically, the pose index will HEAVILY mismatch unless ALL empty poses are indexed properly - NOT what we wanted to happen at all. will need to think of a solution.
                        # })
                        # image_padding_data.append((left_padding, top_padding, right_padding, bottom_padding))
                        image_prep_data.append({
                            "padding": (left_padding, top_padding, right_padding, bottom_padding),
                            "original_layer_index": layer_index, 
                            "original_pose_location": pose_location # pose_location ain't great; it's not really a LOCATION, it's an xy and a size. I dunno.
                        })

                        # if pose_index == 41:
                        #     print(layer["name"])
                            # bound_image.show()


                        # print("unique image pose location: ", pose_location)
                        # if pose_index > 90: bound_image.show()
                        update_progress(None, f"Unique images found: {len(image_prep_data)}")

                    # if making automatic padding, either minimize or maximize. don't need to do this when no auto-padding, since all sides will be equal.
                    elif generation_data["automatic_padding_type"] != "None": 
                                
                        if is_flipped:
                            temp = left_padding
                            left_padding = right_padding
                            right_padding = temp

                        paddings = [left_padding, top_padding, right_padding, bottom_padding]

                        # Rotate padding values counterclockwise by 90-degree steps
                        # could definitely make its own function, but then i'd have to worry about the clockwise stuff, and... eh
                        for _ in range(rotation_amount):
                            paddings = [paddings[1], paddings[2], paddings[3], paddings[0]]

                        left_padding, top_padding, right_padding, bottom_padding = paddings

                        match generation_data["automatic_padding_type"]: # probably an even more efficient way to do this
                            case "Show only always-visible pixels":
                                left_padding = min(image_prep_data[image_index]["padding"][0], left_padding)
                                top_padding = min(image_prep_data[image_index]["padding"][1], top_padding)
                                right_padding = min(image_prep_data[image_index]["padding"][2], right_padding)
                                bottom_padding = min(image_prep_data[image_index]["padding"][3], bottom_padding)
                            case "Show all theoretically-visible pixels":
                                left_padding = max(image_prep_data[image_index]["padding"][0], left_padding)
                                top_padding = max(image_prep_data[image_index]["padding"][1], top_padding)
                                right_padding = max(image_prep_data[image_index]["padding"][2], right_padding)
                                bottom_padding = max(image_prep_data[image_index]["padding"][3], bottom_padding)
                        
                        image_prep_data[image_index]["padding"] = (left_padding, top_padding, right_padding, bottom_padding)

                    limb = {
                        "name": curr_layer_name,
                        "x_offset": bbox[0], # do we WANT this to be set at the moment? i mean... YES, right? i dunno.
                        "y_offset": bbox[1],
                        "image_index": image_index,
                        "flip_h": is_flipped,
                        "rotation_amount": rotation_amount # REMEMBER that you changed "rotation" to "rotation_amount" here recently (6/4/25)!!!
                    }

                    limb_data.append(limb)

        if len(limb_data) or generation_data["generate_empty_poses"]:
            pose_data.append({
                "name": f"pose_{pose_location['x_position']}_{pose_location['y_position']}",
                "x_position": pose_location["x_position"],
                "y_position": pose_location["y_position"],
                "width": pose_location["width"],
                "height": pose_location["height"],
                "limb_data": limb_data
            })
        
        #TODO: this. the one at the top, too
        update_progress(math.floor((pose_index / len(pose_locations) * 100)))
    
    # THIS is where we'll need to do a search through the limbs to change the offsets, unfortunately. good news is, we SHOULDN'T need to open the images again -
    # the necessary data SHOULD be stored in image_prep_data.
    for pose in pose_data:
        for limb in pose["limb_data"]:
            # padding is called "paddings" somewhere above, fix probably
            padding = image_prep_data[limb["image_index"]]["padding"]
            limb["x_offset"] -= padding[0]
            limb["y_offset"] -= padding[1]
            # LIKELY will not work until i figure out why not all images are getting exported

    for image in layer_search_images:
        image.close()
    
    # print(len(image_prep_data))

    return pose_data, image_prep_data

def generate_image_data(image_prep_data, layer_data, pose_data, update_progress):

    update_progress(0, "Generating images...")
    images = []
    image_data = []
    number_of_characters = len(str(len(image_prep_data)))

    # opening layer images here so that we don't have to re-open and -close them over and over 
    layer_search_images = []
    layer_source_images = []

    for layer in layer_data:
        # I think there's probably a more efficient way to do this, but I don't wanna

        # If there's a search image, add it. If not, add None just to keep indexes correct
        if layer.get("search_image_path"):
            layer_search_images.append(Image.open(layer["search_image_path"]))
        else:
            layer_search_images.append(None)

        # Same as above
        if layer.get("source_image_path"):
            layer_source_images.append(Image.open(layer["source_image_path"]))
        else:
            layer_source_images.append(None)
    
    image_data = []
    for i, image_prep in enumerate(image_prep_data):
        # image = image_object["img"]
        padding = image_prep["padding"]
        layer_index = image_prep["original_layer_index"]
        original_pose_location = image_prep["original_pose_location"]

        crop_box = (original_pose_location["x_position"], original_pose_location["y_position"], original_pose_location["width"] + original_pose_location["x_position"] - 1, original_pose_location["height"] + original_pose_location["y_position"] - 1)

        # search_image = None
        # source_image = None
        # output_image = None

        search_image = layer_search_images[layer_index].crop(crop_box)
        search_image_bbox = search_image.getbbox()
        bound_search_image = search_image.crop(search_image_bbox)

        

        # if layer_data[layer_index]["layer_search_image"]: # TODO: at some point SOON, rename to layer_search_image_path or search_image_path. do the same for source
        #     search_image = layer_search_images[layer_index].crop((original_pose_location[0], original_pose_location[1], original_pose_location[2] + original_pose_location[0], original_pose_location[3] + original_pose_location[1]))
        # else:
        #     output_image = layer_source_images[layer_index].crop((original_pose_location[0], original_pose_location[1], original_pose_location[2] + original_pose_location[0], original_pose_location[3] + original_pose_location[1])) # DOES NOT WORK if this doesnt have a source image. i'm not sure what i'm even doing, honestly. REALLY mad tired.

        # if layer_data[layer_index]["layer_source_image"]:
        #     source_image = layer_source_images[layer_index].crop((original_pose_location[0], original_pose_location[1], original_pose_location[2] + original_pose_location[0], original_pose_location[3] + original_pose_location[1]))
        # else:
        #     output_image = layer_search_images[layer_index].crop((original_pose_location[0], original_pose_location[1], original_pose_location[2] + original_pose_location[0], original_pose_location[3] + original_pose_location[1]))
        
        # if output_image != None: # TODO TODO TODO ok I REALLY need to stop for the day. WAY too tired. HEY DUMBSKULL, START HERE TOMORROW (6/4/2025) TODO TODO TODO
        #     padded_image = Image.new("RGBA", ((output_image.width + padding[0] + padding[2]), (output_image.height + image_top_padding + image_bottom_padding)), color_transparent)
        #     images.append(output_image)

        # if layer_data[layer_index]["layer_search_image"] and layer_data[layer_index]["layer_source_image"]:
        #     pass
        # elif layer_data[layer_index]["layer_search_image"]:
        #     pass
        # elif layer_data[layer_index]["layer_source_image"]:

        # print(str(image_bottom_padding))
        # print(str(image_bottom_padding))
        # print(str(image_bottom_padding))
        # print(str(image_bottom_padding))

        # padded_image = Image.new("RGBA", ((image.width + image_left_padding + image_right_padding), (image.height + image_top_padding + image_bottom_padding)), color_transparent)
        color_transparent = ImageColor.getrgb("#00000000")

        # - bbox + padding (thats kinda already what im doin)

        padded_image = Image.new("RGBA", ((bound_search_image.width + padding[0] + padding[2]), (bound_search_image.height + padding[1] + padding[3])), color_transparent)
        # padded_image.paste(image, (image_left_padding, image_top_padding))


        # get original pose that has this image
        # get bbox for this new padded_image
        # get bbox for original pose's version of the image
        # compare original pose's version's bbox to bbox for source version of image
        # factoring in necessary adjustments, add padded_image's bbox appropriately

        # TEMP_x = TEMP_image_original_pose_data[image_index]["x_position"]
        # TEMP_y = TEMP_image_original_pose_data[image_index]["y_position"]
        # TEMP_w = TEMP_image_original_pose_data[image_index]["width"]
        # TEMP_h = TEMP_image_original_pose_data[image_index]["height"]
        # TEMP_layer = TEMP_image_original_pose_data[image_index]["layer_index"]

        # print(TEMP_layer)

        # original_pose_image = layer_images[TEMP_layer].crop((TEMP_x, TEMP_y, TEMP_x + TEMP_w, TEMP_y + TEMP_h))
        # source_image = layer_image_sources[TEMP_layer].crop((TEMP_x, TEMP_y, TEMP_x + TEMP_w, TEMP_y + TEMP_h))
        # these SHOULD be the same size

        # final_output_image = padded_image.copy()

        # source_image = None
        source_image = search_image
        # source_image_bbox = None
        source_image_bbox = search_image_bbox

        if layer_data[layer_index].get("source_image_path"):
            source_image = layer_source_images[layer_index].crop(crop_box)
            source_image_bbox = source_image.getbbox()
            # bound_source_image = source_image.crop(source_image_bbox)
            # i feel like this might cause problems???

        # else:
            # source_image = search_image#could just do stuff and return here i guess
        
        x_offset = padding[0] - search_image_bbox[0]
        y_offset = padding[1] - search_image_bbox[1]
        # x_offset = padding[0] - source_image_bbox[0]
        # y_offset = padding[1] - source_image_bbox[1]
        padded_image.paste(source_image, (x_offset, y_offset))
        images.append(padded_image)

        original_pose_index = None

        # honestly? should throw an error if it tries to find a pose that doesn't exist
        for original_pose_index, pose in enumerate(pose_data):
            # if image_prep_data[i]["original_pose_location"][0] in 
            if pose["x_position"] == original_pose_location["x_position"] and pose["y_position"] == original_pose_location["y_position"]:
                # original_pose_index = pose_index
                break
        
        # original_pose_index = [pose_index for pose_index, pose in enumerate(pose_data)]

        # ok so I THINK we need to reduce each limb's offset sometime here! but where????

        image_data.append({
            "path": f"{str(i).rjust(number_of_characters, '0')}.png",
            # "original_layer_index": image_prep_data[i]["original_layer_index"],
            "original_layer_index": image_prep["original_layer_index"],
            # "original_pose_index": image_prep_data[i]["original_pose_index"]
            "original_pose_index": original_pose_index
        })

        update_progress(math.floor((len(images) / len(image_prep_data) * 100)), "Generating images...")

        # if original_pose_image.tobytes() == source_image.tobytes(): #could instead check if source img is same as search img
        #     final_output_image.paste(image, (image_left_padding, image_top_padding))
        # else:
        #     original_pose_bbox = original_pose_image.getbbox()

        #     if original_pose_bbox: # NOT a problem, because there cannot NOT be an original pose
        #         source_bbox = source_image.getbbox()
        #         # theoretically different sizes

        #         if source_bbox:

        #             #if the original image is BIGGER THAN the source image, then the original image's bbox is SMALLER THAN the source image's bbox
        #             #if the original image is SMALLER THAN the source image, then the original image's bbox is BIGGER THAN the source image's bbox

        #             # new_bbox = (source_bbox[0] - original_pose_bbox[0], source_bbox[1] - original_pose_bbox[1], source_bbox[2] - original_pose_bbox[2], source_bbox[3] - original_pose_bbox[3])

        #             # image_left_padding = image_left_padding + new_bbox[0]
        #             # image_top_padding = image_top_padding + new_bbox[1]

        #             # image_left_padding -= source_bbox[0]
        #             # image_top_padding -= source_bbox[1] # doesnt work ## actually, test again? changed smth. might just wanna do select layer json stuff first to save time

        #             # ok, still causes issues when original_pose and source are diff sizes. also, likely works even worse when rotations/flips involved. (NO, because these are the IMAGES, not the posed limbs, so we're only storing unrotated/unflipped info anyway)
        #             # image_left_padding += original_pose_bbox[0] - source_bbox[0]
        #             # image_top_padding += original_pose_bbox[1] - source_bbox[1]

        #             # image_left_padding -= original_pose_bbox[0]
        #             # image_top_padding -= original_pose_bbox[1]
                    
        #             # image_left_padding += source_bbox[0]
        #             # image_top_padding += source_bbox[1]

        #             image_left_padding -= source_bbox[0]
        #             image_top_padding -= source_bbox[1]

        #             image_left_padding -= original_pose_bbox[0] - source_bbox[0]
        #             image_top_padding -= original_pose_bbox[1] - source_bbox[1]

        #             # final_output_image.paste(source_image.crop(source_bbox), (image_left_padding, image_top_padding))
        #             final_output_image.paste(source_image, (image_left_padding, image_top_padding))


    for image in layer_search_images:
        if image != None: image.close()
        
    for image in layer_source_images:
        if image != None: image.close()


    update_progress(100, "Images generated")

    
    # for i in range(len(image_prep_data)):
    return image_data, images

    # return images

def generate_layer_data(input_layer_data, output_folder_path, paths_are_local):
    output_layer_data = []
    
    for layer in input_layer_data:
        search_image_path = None
        source_image_path = None

        if layer["export_original_images"]:

            if layer["search_image_path"]:
                search_image_path = f"{layer['name']}_search_image.png" if not layer["is_border"] else "border.png"

                with Image.open(layer["search_image_path"]) as search_image:
                    search_image.save(output_folder_path + search_image_path)

                if not paths_are_local: search_image_path = output_folder_path + search_image_path
            if layer["source_image_path"]:
                source_image_path = f"{layer['name']}_source_image.png"

                with Image.open(layer["source_image_path"]) as source_image:
                    source_image.save(output_folder_path + source_image_path)

                if not paths_are_local: source_image_path = output_folder_path + source_image_path

        output_layer_data.append({
            "name": layer["name"], "is_border": layer["is_border"], "is_cosmetic_only": layer["is_cosmetic_only"],
            "search_image_path": search_image_path, "source_image_path": source_image_path
        })

    return output_layer_data

# Return vals: is_unique, is_flippped, rotation_amount
def compare_images(image:Image, compare_to:Image, detect_identical_images = True, detect_rotated_images = True, detect_flip_h_images = True, detect_flip_v_images = False):
    if detect_identical_images and image.tobytes() == compare_to.tobytes(): # the image is already stored; move on
        # print("identical image")
        return False, False, 0

    # a necessary evil, i think
    flip_h = None

    if detect_flip_h_images:
        # prepare a flipped version of the img, since it'll commonly be an already-stored img, and it's in a lotta checks
        flip_h = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        if flip_h.tobytes() == compare_to.tobytes(): # the flipped image is already stored; move on
            # print("flipped image")
            return False, True, 0

    if detect_rotated_images:                    
        # rotate normal image 90 degrees
        if image.transpose(Image.Transpose.ROTATE_90).tobytes() == compare_to.tobytes():
            # print("rot90 image")
            return False, False, 1

        # rotate normal image 180 degrees
        if image.transpose(Image.Transpose.ROTATE_180).tobytes() == compare_to.tobytes():
            # print("rot180 image")
            return False, False, 2

        # rotate normal image 270 degrees
        if image.transpose(Image.Transpose.ROTATE_270).tobytes() == compare_to.tobytes():
            # print("rot270 image")
            return False, False, 3

    if detect_flip_h_images and detect_rotated_images:
        # rotate flipped image 270 degrees (i.e. -90 degrees, 'cause it's flipped)
        if flip_h.transpose(Image.Transpose.ROTATE_270).tobytes() == compare_to.tobytes():
            # print("flip rot270 image")
            return False, True, 3

        # rotate flipped image 180 degrees
        if flip_h.transpose(Image.Transpose.ROTATE_180).tobytes() == compare_to.tobytes():
            # print("flip rot180 image")
            return False, True, 2

        # rotate flipped image 90 degrees (i.e. -270 degrees, 'cause it's flipped)
        if flip_h.transpose(Image.Transpose.ROTATE_90).tobytes() == compare_to.tobytes():
            # print("flip rot90 image")
            return False, True, 1

    elif detect_flip_v_images:
        flip_v = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        if flip_v.tobytes() == compare_to.tobytes(): # the flipped image is already stored; move on
            return False, True, 2 # like flip_h, but just add 2 to rotation (180 degrees) & flip back around if necessary (4 = 0, 5 = 1)

        if detect_rotated_images:
            # rotate flipped image 270 degrees (i.e. -90 degrees, 'cause it's flipped)
            if flip_v.transpose(Image.Transpose.ROTATE_270).tobytes() == compare_to.tobytes():
                return False, True, 1 # so, in total, rotate 270 + 180 = 90 degrees

            # rotate flipped image 180 degrees
            if flip_v.transpose(Image.Transpose.ROTATE_180).tobytes() == compare_to.tobytes():
                return False, True, 0 # so, in total, rotate 180 + 180 = 0 degrees

            # rotate flipped image 90 degrees (i.e. -270 degrees, 'cause it's flipped)
            if flip_v.transpose(Image.Transpose.ROTATE_90).tobytes() == compare_to.tobytes():
                return False, True, 3 # so, in total, rotate 90 + 180 = 270 degrees
    
    # print("unique image")
    # Getting here doesn't mean the image IS unique OVERALL - it still likely has to check against many more images
    return True, False, 0

# I probably should've split this into a few smaller functions. Oh well *shrug*
# padding_type: 0 = minimize (show only pixels that WILL show up on final sheet), 1 = maximize (show ALL pixels that COULD THEORETICALLY end up on sheet), 2 = custom amount
# def GenerateJSON(output_name, border_image_path, border_color, image_info, start_search_in_center = True, search_right_to_left = False, padding_type = 0, custom_padding = 0):

#     # TEMP_header = {
#     #     "name": output_name,
#     #     "consistxels_version": consistxels_version,
#     #     "paths_are_local": True
#     # }

#     # TEMP_layer_data = [
#     #     {"name": "closearm", "is_border": False, "is_cosmetic_only": True, "search_image_path": "closearm.png", "source_image_path": "closearm.png", "export_original_images": False},
#     #     {"name": "farleg", "is_border": False, "is_cosmetic_only": False, "search_image_path": None, "source_image_path": None, "export_original_images": True},
#     #     {"name": "border", "is_border": True, "is_cosmetic_only": True, "search_image_path": "border.png", "source_image_path": None, "export_original_images": True}
#     # ]

#     # TEMP_search_data = {
#     #     "start_search_in_center": True,
#     #     "search_right_to_left": False,
#     #     "detect_identical_images": True, # should we default the other searches to False if this is false? i dunno
#     #     "detect_rotated_images": True,
#     #     "detect_flip_h_images": True,
#     #     "detect_flip_v_images": False
#     # }

#     # TEMP_search_type_data = {
#     #     "search_type": "Border",
#     #     "border_layer_index": 2,
#     #     "border_color": "#00007f",
#     #     "spacing_rows": None,
#     #     "spacing_columns": None,
#     #     "spacing_outer_padding": None,
#     #     "spacing_inner_padding": None,
#     #     "spacing_x_separation": None,
#     #     "spacing_y_separation": None
#     # }

#     # TEMP_generation_data = {
#     #     "automatic_padding_type": "None",
#     #     "custom_padding_amount": 0,
#     #     "generate_empty_poses": False
#     #     # likely some other stuff eventually, i guess like palette stuff??? i dunno
#     # }

#     # TEMP_pose_data = [
#     #     {
#     #         "name": "pose_0_0", "x_position": 0, "y_position": 0,
#     #         "width": 0, "height": 0,
#     #         "limb_data":[
#     #             {
#     #                 "name": "closearm", "layer_index": 0,
#     #                 "x_offset": 0, "y_offset": 0, "image_index": 0,
#     #                 "rotation": 0, "flip_h": False, "flip_v": False
#     #             }
#     #         ]
#     #     }
#     # ]

#     # start_time = time.localtime()
#     # start_time = time()
#     start_time = datetime.now()

#     border_image = Image.open(border_image_path) # get image

#     border_image_array = asarray(border_image) # get image as array

#     height, width = border_image_array.shape[:2] # get height and width of image

#     # get border_color (needs to have an alpha channel)
#     # border_color_rgb = ImageColor.getrgb("#00007fff")
#     border_color_rgb = ImageColor.getrgb(border_color + "ff")

#     # for storing unique images!
#     # specifically, will store the image, and its minimum padding (make min or max padding a setting? just min for now i guess)
#     # format: [{"img", "left_padding", "top_padding", "right_padding", "bottom_padding"}]
#     image_object_array = []

#     # format: [{"x_position", "y_position", "width", "height"}]
#     # or i guess we could just store each's original pose? cause all that's stored there just fine
#     TEMP_image_original_pose_data = []

#     # for storing pose information, which will be output in .json format
#     # format:
#     # [{
#     #   "name",
#     #   "x_position",
#     #   "y_position",
#     #   "width",
#     #   "height",
#     #   "limb_objects" = [{}]
#     # }]
#     pose_objects = []

#     # opening layer images here so that we don't have to re-open and -close them over and over while searching for poses 
#     layer_images = []
#     layer_image_sources = []
#     for layer_data in image_info:
#         layer_image = Image.open(layer_data["path"])

#         # layer_images.append(Image.open(layer_data["path"]))
#         layer_images.append(layer_image)

#         if layer_data["alt_source"]:
#             layer_image_sources.append(Image.open(layer_data["alt_source"]))
#         else:
#             layer_image_sources.append(layer_image)

#     # layer_image_sources = []
#     # for layer_data in image_info:

#     # and for good measure, limb_objects format:
#     # [{"x_offset", "y_offset", "image_index", "flip_h", "rotation"}]
#     # this is specifically limbs that are PART OF a pose, not just saved limb images. so these contain pose-specific data, and are not interchangeable,
#     # even if they reference the same limb image.
#     # also, the image they reference is gonna be a number - and that'll reference the number of images, i think??? like, there are 99 images in
#     # a given images folder, and the number can just double as the filename
#     # also also, "offset" is referring to how far off the top-left corner of the sprite is from the top-left corner of the pose box.
#     # also also also, "flip_h" does what it says on the tin (it's a bool), and "rotation" stores an int, and increments rotation by 90 degrees

#     last_percent = -1 # for printing info during search

#     # always subtracting 2 from the ranges, because there is no pose that can fit in a 2-wide or 2-high box, inclusive of border - there's no space
#     for y in range(height - 2): # rows
#         # This is where the right-to-left searching or left-to-right searching is decided
#         # for x in (range(width - 2, -1, -1) if search_right_to_left else range(width - 2)): # columns
#         for x in (get_x_range(0, width, start_search_in_center, search_right_to_left)): # columns

#             pixel = border_image.getpixel([x,y]) # get the pixel at the current coordinates

#             # coordinates will be set to bottom-right corner of pose box
#             endborder_x = -1
#             endborder_y = -1

#             if pixel == border_color_rgb: # i.e. if the current pixel is part of a pose box border:

#                 # if the current pixel is in the shape of a top-left corner
#                 # (works regardless of whether searching right-to-left or left-to-right)
#                 if border_image.getpixel([x + 1, y]) == border_color_rgb \
#                 and border_image.getpixel([x, y + 1]) == border_color_rgb \
#                 and not border_image.getpixel([x + 1, y + 1]) == border_color_rgb:
                    
#                     # iterate all the way to the right. if no border is found, it's not a pose box after all.
#                     for x2 in range(x + 1, width):
#                         if border_image.getpixel([x2, y + 1]) == border_color_rgb:

#                             endborder_x = x2 # set x position of bottom-right corner
#                             break # no need to keep looking
                    
#                     if endborder_x != -1: # if a border has been found, it's likely a pose box.
                        
#                         for y2 in range(y + 1, height): # look for the bottom right of the pose box.
                            
#                             pixel2 = border_image.getpixel([endborder_x, y2]) # pixel with which to find bottom-right of pose box

#                             if pixel2 != border_color_rgb: break # if a non-border pixel's ever found, it's not a pose box.
                            
#                             # if the current pixel2 is in the shape of a bottom-right corner
#                             if border_image.getpixel([endborder_x - 1, y2]) == border_color_rgb \
#                             and border_image.getpixel([endborder_x, y2 - 1]) == border_color_rgb \
#                             and not border_image.getpixel([endborder_x - 1, y2 - 1]) == border_color_rgb: #pose box found!

#                                 endborder_y = y2 # set y position of bottom-right corner
#                                 break # no need to keep looking
        
#             # i.e. if there's a valid bottom-right corner (which guarantees, for our purposes, that there really is a pose box)
#             if endborder_x >= 0 and endborder_y >= 0:

#                 # We COULD not save completely-empty poses. TODO: think about this more. Would need to go much later - i.e. where they're actually saved
#                 # But there IS value in making pose box json even if there's no sprite there. After all, the box is still there in the provided
#                 # border, at least.

#                 # x and y coordinate are moved right and down 1, so that they're INSIDE the pose box, rather than on its border
#                 found_pose_x = x + 1
#                 found_pose_y = y + 1
#                 found_pose_width = endborder_x - x - 1
#                 found_pose_height = endborder_y - y - 1

#                 # creation of pose object
#                 pose_object = {
#                     "name": "pose_" + str(found_pose_x) + "_" + str(found_pose_y), # maybe think of better name?
#                     "x_position": found_pose_x,
#                     "y_position": found_pose_y,
#                     "width": found_pose_width,
#                     "height": found_pose_height,
#                     "limb_objects": []
#                 }
                
#                 layer_index = 0 # i hate this so much i gotta go eat dinner

#                 # now, search through every layer for sprites
#                 for layer_data in image_info:

#                     # we already opened the layer images provided, so that we don't have to open and close them every time we find a pose box
#                     curr_layer_image = layer_images[layer_index]
#                     # layer_index += 1
                    
#                     curr_layer_name = layer_data["name"]

#                     # crop parameter tuple: (left, top, right, bottom)
#                     test_val_tuple = (found_pose_x, found_pose_y, endborder_x, endborder_y) # not endborder_x - 1, for some reason. cut off a pixel that way

#                     unbound_image = curr_layer_image.crop(test_val_tuple) # the full image inside the pose box

#                     # testimg = Image.new("RGBA", (2,2))
#                     # testimg.transpose()

#                     # the rectangle inside the image that actually contains a sprite - everything else is just transparent pixels
#                     bbox = unbound_image.getbbox()
#                     # print(bbox)
                    
#                     # getbbox() returns None if there's no sprite, so this is verifying that there's even a sprite in the first place
#                     if bbox:
#                         # store info implied by bounding box - i.e. offset. this is for formatting purposes in export, BUT ALSO for deciding maximum bounds for each limb

#                         # crop image down to bounding box, so that it can be compared to other stored images
#                         bound_image = unbound_image.crop(bbox)
                        
#                         # loop control
#                         image_is_unique = True
#                         image_index = 0

#                         # info for posed limbs, declared outside the loop so that they persist, but i dunno if python works like that
#                         is_flipped = False # whether the image is flipped horizontally
#                         rotation_amount = 0 # increment by 1, each represents 90 degrees

#                         # check against stored images - check w/ flip_h, flip_y, & rotate. so like 12 checks per limb :(
#                         for data in image_object_array:

#                             img = data["img"] # get img from 

#                             if bound_image.tobytes() == img.tobytes(): # the bound image is already stored; move on
#                                 image_is_unique = False
#                                 break
                            
#                             # prepare a flipped version of the img, since it'll commonly be an already-stored img, and it's in a lotta checks
#                             flip_h = bound_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                            
#                             if flip_h.tobytes() == img.tobytes(): # the flipped image is already stored; move on
#                                 image_is_unique = False
#                                 is_flipped = True
#                                 break
                            
#                             # rotate normal image 90 degrees
#                             if bound_image.transpose(Image.Transpose.ROTATE_90).tobytes() == img.tobytes():
#                                 image_is_unique = False
#                                 rotation_amount = 1
#                                 break

#                             # rotate normal image 180 degrees
#                             if bound_image.transpose(Image.Transpose.ROTATE_180).tobytes() == img.tobytes():
#                                 image_is_unique = False
#                                 rotation_amount = 2
#                                 # print(curr_layer_name, bbox)
#                                 break

#                             # rotate normal image 270 degrees
#                             if bound_image.transpose(Image.Transpose.ROTATE_270).tobytes() == img.tobytes():
#                                 image_is_unique = False
#                                 rotation_amount = 3
#                                 break
                            
#                             # rotate flipped image 270 degrees (i.e. -90 degrees, 'cause it's flipped)
#                             if flip_h.transpose(Image.Transpose.ROTATE_270).tobytes() == img.tobytes():
#                                 image_is_unique = False
#                                 is_flipped = True
#                                 rotation_amount = 3
#                                 break

#                             # rotate flipped image 180 degrees
#                             if flip_h.transpose(Image.Transpose.ROTATE_180).tobytes() == img.tobytes():
#                                 image_is_unique = False
#                                 is_flipped = True
#                                 rotation_amount = 2
#                                 break

#                             # rotate flipped image 90 degrees (i.e. -270 degrees, 'cause it's flipped)
#                             if flip_h.transpose(Image.Transpose.ROTATE_90).tobytes() == img.tobytes():
#                                 image_is_unique = False
#                                 is_flipped = True
#                                 rotation_amount = 1
#                                 break
                            
#                             # LUCKILY FOR ME, don't need to check flip_v at all. It's equivalent to flip_h rotate 180 degrees. All rotations for flip have
#                             # been checked, so no need to check flip_v.

#                             image_index += 1

#                         # padding is saved for a few reasons. mostly, it's there to make the sprites easier to edit in a separate program once
#                         # they've been output. without the padding, there'd be no room to work with, and you'd need to increase the size of the sprites,
#                         # and then everything would get cut off, and it'd just be a whole mess. minimum padding was chosen because it shows exactly
#                         # where the padding can be such that nothing gets cut off, in any of the poses where the identical image is used. however,
#                         # maximum padding, wherein one can choose to see maximum space available for even a single pose, even if it gets cut off,
#                         # will also be available. as will custom padding values!!! so that's fun. TODO: make comment better

#                         # print("\n", bbox)

                        
#                         # left_padding = bbox[0]
#                         # top_padding = bbox[1]
#                         # right_padding = unbound_image.width - (left_padding + bound_image.width)
#                         # print(bbox[2], bound_image.width)
#                         # bottom_padding = unbound_image.height - (top_padding + bound_image.height) # maybe issue is here????????????

#                         # right_padding = unbound_image.width - bbox[2]
#                         # bottom_padding = unbound_image.height - bbox[3]

#                         # match padding_type:
#                         #     case 2:
#                         #         left_padding, top_padding, right_padding, bottom_padding = custom_padding
#                         #     case _:
#                         #         left_padding = bbox[0]
#                         #         top_padding = bbox[1]
#                         #         right_padding = unbound_image.width - bbox[2]
#                         #         bottom_padding = unbound_image.height - bbox[3]
                        
#                         # print(custom_padding, type(custom_padding))
#                         left_padding = top_padding = right_padding = bottom_padding = custom_padding

#                         if padding_type != 2:
#                             left_padding += bbox[0]
#                             top_padding += bbox[1]
#                             right_padding += unbound_image.width - bbox[2]
#                             bottom_padding += unbound_image.height - bbox[3]

#                         left_padding = max(0, left_padding)
#                         top_padding = max(0, top_padding)
#                         right_padding = max(0, right_padding)
#                         bottom_padding = max(0, bottom_padding)

#                         # left_padding, top_padding, right_padding, bottom_padding = bbox

#                         if image_is_unique:
#                             image_object_array.append({
#                                 "img": bound_image,
#                                 "width": bound_image.width,
#                                 "height": bound_image.height,
#                                 "left_padding": left_padding,
#                                 "top_padding": top_padding,
#                                 "right_padding": right_padding,
#                                 "bottom_padding": bottom_padding
#                             })

#                             # test for a feature that will likely never be used by anyone but me but i will get GREAT use out of it
#                             TEMP_image_original_pose_data.append({
#                                 "x_position": found_pose_x,
#                                 "y_position": found_pose_y,
#                                 "width": found_pose_width,
#                                 "height": found_pose_height,
#                                 "layer_index": layer_index
#                             })
#                         # if making automatic padding, either minimize or maximize. don't need to do this for custom padding, since it'll be equal;
#                         # rotating and flipping would do nothing
#                         elif padding_type != 2: 
                            
#                             if is_flipped:
#                                 temp = left_padding
#                                 left_padding = right_padding
#                                 right_padding = temp

#                             paddings = [left_padding, top_padding, right_padding, bottom_padding]

#                             # Rotate padding values counterclockwise by 90-degree steps
#                             # could definitely make its own function, but then i'd have to worry about the clockwise stuff, and... eh
#                             for _ in range(rotation_amount):
#                                 paddings = [paddings[1], paddings[2], paddings[3], paddings[0]]

#                             left_padding, top_padding, right_padding, bottom_padding = paddings

#                             match padding_type: # probably an even more efficient way to do this
#                                 case 0:
#                                     image_object_array[image_index]["left_padding"] = min(image_object_array[image_index]["left_padding"], left_padding)
#                                     image_object_array[image_index]["top_padding"] = min(image_object_array[image_index]["top_padding"], top_padding)
#                                     image_object_array[image_index]["right_padding"] = min(image_object_array[image_index]["right_padding"], right_padding)
#                                     image_object_array[image_index]["bottom_padding"] = min(image_object_array[image_index]["bottom_padding"], bottom_padding)
#                                 case 1:
#                                     image_object_array[image_index]["left_padding"] = max(image_object_array[image_index]["left_padding"], left_padding)
#                                     image_object_array[image_index]["top_padding"] = max(image_object_array[image_index]["top_padding"], top_padding)
#                                     image_object_array[image_index]["right_padding"] = max(image_object_array[image_index]["right_padding"], right_padding)
#                                     image_object_array[image_index]["bottom_padding"] = max(image_object_array[image_index]["bottom_padding"], bottom_padding)

#                             # if image_object_array[image_index]["left_padding"] > left_padding:
#                             #     image_object_array[image_index]["left_padding"] = left_padding
#                             # if image_object_array[image_index]["top_padding"] > top_padding:
#                             #     image_object_array[image_index]["top_padding"] = top_padding
#                             # if image_object_array[image_index]["right_padding"] > right_padding:
#                             #     image_object_array[image_index]["right_padding"] = right_padding
#                             # if image_object_array[image_index]["bottom_padding"] > bottom_padding:
#                             #     image_object_array[image_index]["bottom_padding"] = bottom_padding

#                         # limb_object = {
#                         #     "name": curr_layer_name,
#                         #     "x_offset": left_padding, # PRETTY SURE this is correct. these padding variables are unaltered, and have to do with the unbound image
#                         #     "y_offset": top_padding,
#                         #     "image_index": image_index,
#                         #     "flip_h": is_flipped,
#                         #     "rotation": rotation_amount
#                         # }

#                         limb_object = {
#                             "name": curr_layer_name,
#                             "x_offset": bbox[0], # guess what ISN'T fucking unaltered, dipshit (if i forget to delete this comment and someone sees it: this took me 12 hours to figure out)
#                             "y_offset": bbox[1],
#                             "image_index": image_index, # might be a good idea to NOT have this rely on image index. while faster, it means reorganizing pose images will be much tougher. on the other hand, renaming them is massively simple.
#                             "flip_h": is_flipped,
#                             "rotation": rotation_amount
#                         }

#                         pose_object["limb_objects"].append(limb_object)

#                     # and HERE'S where layer stuff stops mattering

#                     layer_index += 1

#                 # some sort of dialog box that updates with what's currently going on, maybe? like a "Poses: ###"

#                 pose_objects.append(pose_object)
#                 # print("Poses found: " + str(len(pose_objects)))

#         # print("Search: " + str(math.floor((y / (height - 2)) * 100)) + "%")
#         curr_percent = math.floor((y / (height - 2)) * 100)
#         if curr_percent > last_percent:
#             print("Search: " + str(curr_percent) + "%\tPoses found: " + str(len(pose_objects)) + "\tUnique images found: " + str(len(image_object_array)))
#             last_percent = curr_percent

#     print("Search: 100%\tPoses found: " + str(len(pose_objects)) + "\tUnique images found: " + str(len(image_object_array)))
    
#     # end_time = time.localtime()
#     end_time = datetime.now()
#     time_elapsed = end_time - start_time
#     time_elapsed_seconds = int(time_elapsed.total_seconds())
#     hours = time_elapsed_seconds // 3600
#     minutes = (time_elapsed_seconds % 3600) // 60
#     seconds = time_elapsed_seconds % 60
#     formatted = f"{hours:02}:{minutes:02}:{seconds:02}"
    
#     print("Search complete! Time elapsed: " + formatted)

#     # ask for output location
#     output_folder_path = filedialog.askdirectory(title="Select an output folder")

#     # output_folder_path = output_folder_path.rstrip("/consistxels_output_" + output_name)
#     # output_folder_path += "/consistxels_output_" + output_name

#     # and then, here, we go through all poses, and all limbs, to update their padding according to the image index listed in the limb_object

#     # go through pose list
#     # - go through limb list
#     # - reference img index's padding
#     # - subtract left padding from x-offset, and top padding from y-offset
#     for pose in pose_objects:
#         for limb in pose["limb_objects"]:
#             image_object = image_object_array[limb["image_index"]]

#             image_left_padding = image_object["left_padding"]
#             image_top_padding = image_object["top_padding"]
#             image_right_padding = image_object["right_padding"]
#             image_bottom_padding = image_object["bottom_padding"]
            
#             if limb["flip_h"]:
#                 temp = image_left_padding
#                 image_left_padding = image_right_padding
#                 image_right_padding = temp

#                 paddings = [image_left_padding, image_top_padding, image_right_padding, image_bottom_padding]
                
#                 # Rotate padding values counterclockwise by 90-degree steps
#                 for _ in range(limb["rotation"]):
#                     paddings = [paddings[1], paddings[2], paddings[3], paddings[0]]
            
#                 image_left_padding, image_top_padding, image_right_padding, image_bottom_padding = paddings
#             else: 
#                 paddings = [image_left_padding, image_top_padding, image_right_padding, image_bottom_padding]

#                 # Rotate padding values clockwise by 90-degree steps
#                 for _ in range(limb["rotation"]):
#                     paddings = [paddings[3], paddings[0], paddings[1], paddings[2]]

#                 image_left_padding, image_top_padding, image_right_padding, image_bottom_padding = paddings

#             limb["x_offset"] -= image_left_padding
#             limb["y_offset"] -= image_top_padding

#             # match rotation_amount:
#             #     case 1:
#             #         temp = image_left_padding
#             #         image_left_padding = image_bottom_padding
#             #         image_bottom_padding = image_right_padding
#             #         image_right_padding = image_top_padding
#             #         image_top_padding = temp
#             #     case 2:
#             #         temp = image_top_padding
#             #         image_top_padding = image_bottom_padding
#             #         image_bottom_padding = temp
#             #         temp = image_left_padding
#             #         image_left_padding = image_right_padding
#             #         image_right_padding = temp
#             #     case 3:
#             #         temp = image_left_padding
#             #         image_left_padding = image_top_padding
#             #         image_top_padding = image_right_padding
#             #         image_right_padding = image_bottom_padding
#             #         image_bottom_padding = temp


#             # x_offset_adjust = -image_left_padding
#             # y_offset_adjust = -image_top_padding


#             # if (image_object["width"] % 2 != 0 or image_object["height"] % 2 != 0) and (limb["rotation"] == 2):
#                 # y_offset_adjust -= 1

#             # limb["x_offset"] += x_offset_adjust
#             # limb["y_offset"] += y_offset_adjust





#     print("Limb offsets adjusted for padding")

#     # go through img list
#     # - update img size using padding
#     # - save imgs!!! we'll need an output folder location, etc.
#     color_transparent = ImageColor.getrgb("#00000000")
#     number_of_characters = len(str(len(image_object_array)))

#     image_index = 0

#     # format: [image_path]
#     images = []

#     for image_object in image_object_array:
#         image = image_object["img"]
#         image_left_padding = image_object["left_padding"]
#         image_top_padding = image_object["top_padding"]
#         image_right_padding = image_object["right_padding"]
#         image_bottom_padding = image_object["bottom_padding"]

#         # print(str(image_bottom_padding))
#         # print(str(image_bottom_padding))
#         # print(str(image_bottom_padding))
#         # print(str(image_bottom_padding))

#         padded_image = Image.new("RGBA", ((image.width + image_left_padding + image_right_padding), (image.height + image_top_padding + image_bottom_padding)), color_transparent)
#         # padded_image.paste(image, (image_left_padding, image_top_padding))


#         # get original pose that has this image
#         # get bbox for this new padded_image
#         # get bbox for original pose's version of the image
#         # compare original pose's version's bbox to bbox for source version of image
#         # factoring in necessary adjustments, add padded_image's bbox appropriately

#         TEMP_x = TEMP_image_original_pose_data[image_index]["x_position"]
#         TEMP_y = TEMP_image_original_pose_data[image_index]["y_position"]
#         TEMP_w = TEMP_image_original_pose_data[image_index]["width"]
#         TEMP_h = TEMP_image_original_pose_data[image_index]["height"]
#         TEMP_layer = TEMP_image_original_pose_data[image_index]["layer_index"]

#         # print(TEMP_layer)

#         original_pose_image = layer_images[TEMP_layer].crop((TEMP_x, TEMP_y, TEMP_x + TEMP_w, TEMP_y + TEMP_h))
#         source_image = layer_image_sources[TEMP_layer].crop((TEMP_x, TEMP_y, TEMP_x + TEMP_w, TEMP_y + TEMP_h))
#         # these SHOULD be the same size

#         final_output_image = padded_image.copy()

#         if original_pose_image.tobytes() == source_image.tobytes(): #could instead check if source img is same as search img
#             final_output_image.paste(image, (image_left_padding, image_top_padding))
#         else:
#             original_pose_bbox = original_pose_image.getbbox()

#             if original_pose_bbox: # NOT a problem, because there cannot NOT be an original pose
#                 source_bbox = source_image.getbbox()
#                 # theoretically different sizes

#                 if source_bbox:

#                     #if the original image is BIGGER THAN the source image, then the original image's bbox is SMALLER THAN the source image's bbox
#                     #if the original image is SMALLER THAN the source image, then the original image's bbox is BIGGER THAN the source image's bbox

#                     # new_bbox = (source_bbox[0] - original_pose_bbox[0], source_bbox[1] - original_pose_bbox[1], source_bbox[2] - original_pose_bbox[2], source_bbox[3] - original_pose_bbox[3])

#                     # image_left_padding = image_left_padding + new_bbox[0]
#                     # image_top_padding = image_top_padding + new_bbox[1]

#                     # image_left_padding -= source_bbox[0]
#                     # image_top_padding -= source_bbox[1] # doesnt work ## actually, test again? changed smth. might just wanna do select layer json stuff first to save time

#                     # ok, still causes issues when original_pose and source are diff sizes. also, likely works even worse when rotations/flips involved. (NO, because these are the IMAGES, not the posed limbs, so we're only storing unrotated/unflipped info anyway)
#                     # image_left_padding += original_pose_bbox[0] - source_bbox[0]
#                     # image_top_padding += original_pose_bbox[1] - source_bbox[1]

#                     # image_left_padding -= original_pose_bbox[0]
#                     # image_top_padding -= original_pose_bbox[1]
                    
#                     # image_left_padding += source_bbox[0]
#                     # image_top_padding += source_bbox[1]

#                     image_left_padding -= source_bbox[0]
#                     image_top_padding -= source_bbox[1]

#                     image_left_padding -= original_pose_bbox[0] - source_bbox[0]
#                     image_top_padding -= original_pose_bbox[1] - source_bbox[1]

#                     # final_output_image.paste(source_image.crop(source_bbox), (image_left_padding, image_top_padding))
#                     final_output_image.paste(source_image, (image_left_padding, image_top_padding))



        

#         # image_path = output_folder_path + "/" + str(image_index).rjust(number_of_characters, "0") + ".png" # TODO: rather than saving relative path, just save image name. we already have the output folder!
#         image_path = str(image_index).rjust(number_of_characters, "0") + ".png"
#         images.append(image_path)
#         # TODO: in GENERAL, the path stuff is... not my favorite. it's really dependant on the user's individual machine, and is therefore unable to be shared around. i COULD separately share the images, pose_objects, etc., that would be fine. i dunno. header relies on absolute paths for the border image, too. maybe that should just be included with the output?
#         # (similarly: don't even NEED the layer paths, if ya think about it, only the names!)

#         # padded_image.save(output_folder_path + "/" + image_path)
#         final_output_image.save(output_folder_path + "/" + image_path)
        
#         image_index += 1
    
#     print("Saved images")

#     # create object with .json "header": maybe the paths of the images used, and the path for the output folder

#     # header = {
#     #     "output_folder_path": output_folder_path,
#     #     "border_image_path": border_image_path,
#     #     "border_color": border_color,
#     #     "image_info": image_info,
#     #     "search_right_to_left": search_right_to_left
#     # }

#     layer_names = [layer["name"] for layer in image_info]

#     layer_data = []

#     for layer in image_info:
#         layer_data.append({"name": layer["name"], "search_image_path": layer["path"], "source_image_path": layer["alt_source"]}) # plus is_cosmetic and is_border

#     json_output = {
#         "header": {
#             "name": output_name,
#             "consistxels_version": consistxels_version,
#             # "output_folder_path": output_folder_path,
#             # "date_generated": date.today(),
#             # "border_image_path": border_image_path,
#             # "border_image_path": output_folder_path + "/border.png",
#             "border_image_path": "border.png",
#             "border_color": border_color,
#             "layer_names": layer_names,
#             "start_search_in_center": start_search_in_center,
#             "search_right_to_left": search_right_to_left
#         },
#         # search data
#         # generation data
#         "pose_objects": pose_objects,
#         "images": images
#         # layer data
#     }
    
#     json_filename = "/consistxels_pose_output_" + output_name + ".json"

#     with open(output_folder_path + json_filename, 'w') as file:
#         # json.dump(pose_object_array, file, indent=4)
#         json.dump(json_output, file, indent=4)

#     print("Saved .json output")

#     border_image.save(output_folder_path + "/border.png") # TODO: WORK ON MORE. GET LOADING TO LOOK AT THIS INSTEAD!
#     border_image.close()

#     for layer_image_source in layer_image_sources:
#         if not layer_image_source in layer_images:
#             layer_image_source.close()

#     for layer_image in layer_images:
#         layer_image.close()
    
    
#     print("Success!")

    # FOR NEXT TIME:
    # - clean up comments some more
    # - add some sort of intuitive progress indicator?
    # - add some sort of CLEAN way to name the images, and associate names with the images. might have to do that INSTEAD OF indexes, but i dunno
    #   - if i do it this way, will NEED to have some sort of editor within the program, and that's out of scope for now
    # 
    # BIG THINGS FOR NEXT TIME:
    # - add a way to upload a .json and have it be able to compile everything! it should have a choice to export individual layers, or the whole image at once.

# fiddling with this a bit; technically, it's not good to so this without adding a setting, but... it's better anyway, and i WILL add the setting.
# TODO: Change "search right to left" into "Reverse search order", and I guess change "Start search in center" to "search outward"?
# It'd be *good* to have that as a setting and keep the original implementation, but... not necessary.
#
# I actually don't need to do that I think, at least not right now. In any case, maybe I should make this more interesting than just an if-else ladder? I dunno.
def get_x_range(start = 0, end = 10, start_search_in_center = False, search_right_to_left = False, edge_offset = 0): # edge_offset modifies the end value without changing the original midpoint
    if start_search_in_center: # if we're starting search in center, we need a chain of ranges, rather than just a range
        # Calculate midpoint
        width = end - start
        midpoint = math.ceil(float(width) / 2.0) + start
        if width % 2: midpoint -= 1

        # Ranges are the same whether it's l2r or r2l, they're just switched
        left_range = range(midpoint - 1, start - 1, -1)
        right_range = range(midpoint, end + edge_offset)

        if not search_right_to_left:
            # return chain(range(midpoint, end + edge_offset), range(midpoint - 1, start - 1, -1)) # Will iterate rightward from center, then leftward from center
            return chain(right_range, left_range) # Will iterate rightward from center, then leftward from center
        else:
            # return chain(range(midpoint - 1, start - 1, -1), range(midpoint, end + edge_offset)) # Will iterate leftward from center, then rightward from center
            return chain(left_range, right_range) # Will iterate leftward from center, then rightward from center
    else:
        if not search_right_to_left:
            return range(start, end + edge_offset) # Will iterate righward from leftmost edge
        else:
            return range(end + edge_offset - 1, start - 1, -1) # Will iterate leftward from rightmost edge