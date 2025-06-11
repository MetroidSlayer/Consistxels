import math
import json
import os

from PIL import Image, ImageColor
from itertools import chain
from datetime import datetime

from shared import consistxels_version

def update_progress(type="update", value = None, header_text = None, info_text = None):
    update = {"type": type, "value": value, "header_text": header_text, "info_text": info_text}
    print(json.dumps(update), flush=True)

# Generate and save a full .json output file, and save all generated pose images
# def generate_all(input_data, output_folder_path, progress_callback = None): #input_data is already in proper structure for consistxels .json
# def generate_all(input_data, output_folder_path, conn = None): #input_data is already in proper structure for consistxels .json
def generate_all(input_data, output_folder_path): #input_data is already in proper structure for consistxels .json
    # output_folder_path += "/" # Adding it now, 'cause otherwise we'd just add it literally every time we use it
    try:
        # p = psutil.Process(os.getpid())
        # p.nice(psutil.HIGH_PRIORITY_CLASS)  # On Windows, boost priority


        output_dir = os.path.abspath(output_folder_path)
        os.makedirs(output_dir, exist_ok=True)

        # print(input_data, output_folder_path)

        # search and source layer images should be opened HERE, or perhaps not here but in main thread. transfers should happen w/ everything in bytes.

        start_time = datetime.now() # Time taken to generate is tracked and shown at the end

        # update_progress(progress_callback, 0, "Initializing...") # is Initializing the right word here?
        # update_progress(conn, 0, "", "Initializing...") # is Initializing the right word here?
        # update_progress(conn, 0, "", "Initializing...") # is Initializing the right word here?
        update_progress("update", 0, "", "Initializing...") # is Initializing the right word here?
        # update_progress(progress_callback, 0, "", "Initializing...") # is Initializing the right word here?

        # Variable declaration

        # Taken from input, but updated versions are used in the output
        # input_header = input_data["header"]
        # input_layer_data = input_data["layer_data"]
        # input_pose_data = input_data["pose_data"]

        # # Also taken from input, but simply used in output as they are, with no modification
        # search_data = input_data["search_data"]
        # search_type_data = input_data["search_type_data"]
        # generation_data = input_data["generation_data"]

        # Taken from input, but updated versions are used in the output
        input_header = input_data.get("header")
        input_layer_data = input_data.get("layer_data")
        input_pose_data = input_data.get("pose_data")

        # Also taken from input, but simply used in output as they are, with no modification
        search_data = input_data.get("search_data")
        search_type_data = input_data.get("search_type_data")
        generation_data = input_data.get("generation_data")

        # Size is used in a few places, especially when generating full output in menu_loadjson, so it's calculated and stored in the header.
        # TODO: Throw exception if size is still (0,0) after that. Or I guess if either height or width is still 0, neither should be after all
        size = (0,0)
        layer = next(layer for layer in input_layer_data if (layer.get("search_image_path") or layer.get("source_image_path")))
        with Image.open(layer["search_image_path"] if layer.get("search_image_path") else layer["source_image_path"]) as img:
        # layer = next(layer for layer in input_layer_data if (layer.get("search_image_path") or layer.get("source_image_path")))
        # layer_path = layer["search_image_path"] if layer.get("search_image_path") else layer["source_image_path"]
        # if input_header["paths_are_local"]: layer_path = os.path.join(output_folder_path, layer_path)
        # with Image.open(layer_path) as img:
            size = img.size

        # Match the search type
        match search_type_data["search_type"]:
            case "Border":
                # pose_locations = search_border(search_data, search_type_data, input_layer_data, progress_callback)
                # pose_locations = search_border(search_data, search_type_data, input_layer_data, conn)
                pose_locations = search_border(search_data, search_type_data, input_layer_data)
            case "Spacing":
                # pose_locations = search_spacing(search_data, search_type_data, size, progress_callback) # TODO: Test
                # pose_locations = search_spacing(search_data, search_type_data, size, conn) # TODO: Test
                pose_locations = search_spacing(search_data, search_type_data, size) # TODO: Test
            case "Preset":
                pose_locations = input_pose_data # TODO: Test
            case _:
                pass # TODO: throw exception: invalid search type

        # Output pose data. Also output some image data; I would have liked to separate them, but they're so conceptually intertwined that I don't think it's possible
        # output_pose_data, image_prep_data = generate_pose_data(pose_locations, input_layer_data, search_data, generation_data, progress_callback)
        # output_pose_data, image_prep_data = generate_pose_data(pose_locations, input_layer_data, search_data, generation_data, conn)
        output_pose_data, image_prep_data = generate_pose_data(pose_locations, input_layer_data, search_data, generation_data)

        # Using the pose and image_prep data, generate the final output image_data as well as the actual images
        # image_data, images = generate_image_data(image_prep_data, input_layer_data, output_pose_data, progress_callback)
        # try:
        # image_data, images = generate_image_data(image_prep_data, input_layer_data, output_pose_data, conn)
        image_data, images = generate_image_data(image_prep_data, input_layer_data, output_pose_data)
        # except:
        #     print("exception")
        #     return

        # print("gothere")

        # update_progress(progress_callback, 25, "Wrapping up; saving images...")
        # update_progress(conn, 25, "Wrapping up; saving images...")
        # update_progress(conn, 100, "", "Wrapping up...")
        update_progress("update", 100, "", "Wrapping up...")
        # update_progress(progress_callback, 100, "", "Wrapping up...")
        
        # TODO: May want to think of better way to do this. Definitely works for now, though
        for i in range(len(images)):
            # print("saving image", i)
            # images[i].save(output_folder_path + image_data[i]["path"])

            image_path = os.path.join(output_dir, image_data[i]["path"])
            images[i].save(image_path)

        # print("images saved")

        # update_progress(progress_callback, 50, "Wrapping up; formatting layer data...")
        # update_progress(conn, 50, "Wrapping up; formatting layer data...")

        # Save OUTPUT layer data, useful if any layers are cosmetic-only or a border
        # print("saving layers")
        # output_layer_data = generate_layer_data(input_layer_data, output_folder_path, input_header["paths_are_local"])
        # output_layer_data, search_images, source_images = generate_layer_data(input_layer_data, output_dir, input_header["paths_are_local"])
        output_layer_data, search_images, source_images = generate_layer_data(input_layer_data)

        for i in range(len(search_images)):
            # print("saving image", i)
            # images[i].save(output_folder_path + image_data[i]["path"])
            if search_images[i]:
                
                image_path = output_layer_data[i]["search_image_path"]
                # if input_header["paths_are_local"]: image_path = os.path.join(output_dir, output_layer_data[i]["search_image_path"])
                
                # search_images[i].save(image_path)
                search_images[i].save(os.path.join(output_dir, image_path))

        for i in range(len(source_images)):
            # print("saving image", i)
            # images[i].save(output_folder_path + image_data[i]["path"])
            if source_images[i]:
                
                image_path = output_layer_data[i]["source_image_path"]
                # if input_header["paths_are_local"]: image_path = os.path.join(output_dir, output_layer_data[i]["source_image_path"])
                
                # source_images[i].save(image_path)
                source_images[i].save(os.path.join(output_dir, image_path))

        # update_progress(progress_callback, 75, "Wrapping up; saving output to .json...")
        # update_progress(conn, 75, "Wrapping up; saving output to .json...")

        # Structure output
        output_header = {
            "name": input_header["name"],
            "consistxels_version": consistxels_version,
            # "paths_are_local": input_header["paths_are_local"],
            "paths_are_local": True,
            "width": size[0],
            "height": size[1]
        }

        output_data = {
            "header": output_header,
            "search_data": search_data,
            "search_type_data": search_type_data,
            "generation_data": generation_data,
            "layer_data": output_layer_data,
            "pose_data": output_pose_data,
            "image_data": image_data
        }

        json_filename = "consistxels_pose_output_" + output_header["name"] + ".json"
        json_path = os.path.join(output_dir, json_filename)

        # with open(output_folder_path + json_filename, 'w') as file:
        with open(json_path, 'w') as file:
            json.dump(output_data, file, indent=4)
            # print("saving json")

        # Calculate and format time elapsed
        # print("getting endtime")
        end_time = datetime.now()
        time_elapsed = end_time - start_time
        time_elapsed_seconds = int(time_elapsed.total_seconds())
        hours = time_elapsed_seconds // 3600
        minutes = (time_elapsed_seconds % 3600) // 60
        seconds = time_elapsed_seconds % 60
        formatted_time_elapsed = f"{hours:02}:{minutes:02}:{seconds:02}"
        # print("time elapsed formatted")
        
        # It's a *tad* redundant to have both update_progress and messagebox.showinfo, but I'd like to both display in the window *and* send an OS alert to the user
        # in case they tabbed out while waiting.
        # update_progress(progress_callback, 100, f"Complete! Time elapsed: {formatted_time_elapsed}")
        # print("updating progress one last time")
        # update_progress(conn, 100, "Complete!", f"Time elapsed: {formatted_time_elapsed}")
        update_progress("done", 100, "Complete!", f"Time elapsed: {formatted_time_elapsed}")
        # update_progress(progress_callback, 100, "Complete!", f"Time elapsed: {formatted_time_elapsed}")
        # messagebox.showinfo("Complete!", f"Time elapsed: {formatted_time_elapsed}")

        # if conn != None:
        #     print("sending done through pipe")
        #     conn.send(["done", 100, "Complete!", f"Time elapsed: {formatted_time_elapsed}"])
        #     # time.sleep(0.05)

        #     while True:
        #         if conn.poll(0.1):  # Check every 100ms
        #             msg = conn.recv()
        #             if msg == "ack":
        #                 break
            
        #     conn.close()
    except Exception as e:
        # if conn != None:
        #     conn.send(("error", str(e)))
        # maybe throw another exception? or at least tell user what's going on. might need to be an else for the if conn != None
        update_progress("error", 0, "An error occured", str(e))
        # update_progress(progress_callback, 0, "An error occured", e)

# Gets passed layer_data and finds the border; uses said border to find and return pose locations.
# Could DEFINITELY just pass ONE layer - just the border, we don't need any other layers necessarily.
# TODO: Make work for irregular pose box sizes, maybe as an option?
# def search_border(search_data, search_type_data, layer_data, progress_callback = None):
# def search_border(search_data, search_type_data, layer_data, conn = None):
def search_border(search_data, search_type_data, layer_data):
    # Determine which layer is the border
    border_layer = next(layer for layer in layer_data if layer.get("is_border"))
    # TODO: throw exception if border_layer == None

    # Open the border image
    with Image.open(border_layer["search_image_path"]) as border_image:
        # Get image size (technically, we could take it from earlier, but I'd like this to operate on its own)
        width, height = border_image.size
        # print(width, height)

        curr_percent = 0 # Exists to prevent near-constant calls to update_progress later on
        # update_progress(conn, 0, f"Searching border image for valid pose boxes... (Pose boxes found: 0)")

        # Get color that will be treated as border edge (formatted for Image library, and made opaque)
        # TODO: test if values that already have alpha can make it here, and stop 'em. probably throw error too
        border_color_rgb = ImageColor.getrgb(search_type_data["border_color"] + "ff")

        # errors if these don't exist, I guess??
        start_search_in_center = search_data["start_search_in_center"]
        search_right_to_left = search_data["search_right_to_left"]

        pose_locations = [] # Not full pose data, just the x/y positions and size

        # We're always subtracting 2 from the ranges, because there is no pose that can fit in a 2-wide or 2-high box (inclusive of border) - there's no space
        for y in range(height - 2): # Rows
            for x in (get_x_range(0, width, start_search_in_center, search_right_to_left, -2)): # Columns

                pixel = border_image.getpixel([x,y]) # Get the pixel at the current coordinates

                # Coordinates will be set to bottom-right corner of pose box
                endborder_x = -1
                endborder_y = -1

                if pixel == border_color_rgb: # i.e. if the current pixel is part of a pose box border:
                    # If the current pixel is in the shape of a top-left corner
                    # (Works regardless of whether searching right-to-left or left-to-right)
                    if border_image.getpixel([x + 1, y]) == border_color_rgb \
                    and border_image.getpixel([x, y + 1]) == border_color_rgb \
                    and not border_image.getpixel([x + 1, y + 1]) == border_color_rgb:
                        
                        for x2 in range(x + 1, width): # Iterate all the way to the right. if no border is found, it's not a pose box after all.
                            if border_image.getpixel([x2, y + 1]) == border_color_rgb:

                                endborder_x = x2 # Set x position of bottom-right corner
                                break # No need to keep looking
                        
                        if endborder_x != -1: # If a border has been found, it's likely a pose box.
                            
                            for y2 in range(y + 1, height): # Look for the bottom right of the pose box.
                                
                                pixel2 = border_image.getpixel([endborder_x, y2]) # Pixel with which to find bottom-right of pose box

                                if pixel2 != border_color_rgb: break # If a non-border pixel's ever found, it's not a pose box.
                                
                                # If the current pixel2 is in the shape of a bottom-right corner
                                if border_image.getpixel([endborder_x - 1, y2]) == border_color_rgb \
                                and border_image.getpixel([endborder_x, y2 - 1]) == border_color_rgb \
                                and not border_image.getpixel([endborder_x - 1, y2 - 1]) == border_color_rgb: #pose box found!

                                    endborder_y = y2 # Set y position of bottom-right corner
                                    break # No need to keep looking
            
                    # i.e. if there's a valid bottom-right corner (which guarantees, for our purposes, that there really is a pose box)
                    if endborder_x >= 0 and endborder_y >= 0:

                        # x and y coordinate are moved right and down 1, so that they're INSIDE the pose box, rather than on its border
                        found_pose_x = x + 1
                        found_pose_y = y + 1
                        # found_pose_width = endborder_x - x # Was subtracting 1 from these, but that caused issues... but NOT subtracting 1 caused
                        # found_pose_height = endborder_y - y# OTHER issues later. Added subtraction later. Maybe need to think of re-adding them here?
                        found_pose_width = endborder_x - x - 1# Was subtracting 1 from these, but that caused issues... but NOT subtracting 1 caused
                        found_pose_height = endborder_y - y - 1# OTHER issues later. Added subtraction later. Maybe need to think of re-adding them here?

                        # Pose location appended as object, to fit with formatting of other search types (pose locations are essentially the same
                        # structure as .json pose_data, just with less info)
                        pose_locations.append({
                            "x_position": found_pose_x,
                            "y_position": found_pose_y,
                            "width": found_pose_width,
                            "height": found_pose_height,
                        })

                        # Update progress text
                        # update_progress(conn, None, f"Searching border image for valid pose boxes... (Pose boxes found: {len(pose_locations)})")
            
            # For updating progress bar. To prevent being called constantly, does a little math
            new_percent = math.floor((y / (height - 2)) * 100)
            if new_percent > curr_percent:
                curr_percent = new_percent
                # update_progress(conn, new_percent, "Searching border image for valid pose boxes...", f"(Pose boxes found: {len(pose_locations)})")
                update_progress("update", new_percent, "Searching border image for valid pose boxes...", f"(Pose boxes found: {len(pose_locations)})")
                # update_progress(progress_callback, new_percent, "Searching border image for valid pose boxes...", f"(Pose boxes found: {len(pose_locations)})")
    
    # update_progress(conn, 100, f"Border search complete! (Pose boxes found: {len(pose_locations)})")

    # List of pose objects is returned
    return pose_locations

# Get a list of pose locations from the provided search_data and size
# def search_spacing(search_data, search_type_data, size, progress_callback = None):
# def search_spacing(search_data, search_type_data, size, conn = None):
def search_spacing(search_data, search_type_data, size):
    # Prepare variables
    rows = search_type_data["spacing_rows"]
    columns = search_type_data["spacing_columns"]
    total_poses = rows * columns # For showing progress
    
    curr_percent = 0 # Exists to prevent near-constant calls to update_progress later on
    # update_progress(conn, 0, f"Preparing pose locations... (0/{total_poses})") # Update progress

    # Variable declaration
    outer_padding = search_type_data["spacing_outer_padding"]
    inner_padding = search_type_data["spacing_inner_padding"]
    x_separation = search_type_data["spacing_x_separation"]
    y_separation = search_type_data["spacing_y_separation"]

    # errors if these don't exist, I guess??
    start_search_in_center = search_data["start_search_in_center"]
    search_right_to_left = search_data["search_right_to_left"]

    width, height = size

    # Calculated so that x/y positions can be properly found
    sprite_width = math.floor((width - (outer_padding * 2) - ((inner_padding * 2) * columns) - (x_separation * (columns - 1))) / columns)
    sprite_height = math.floor((height - (outer_padding * 2) - ((inner_padding * 2) * rows) - (y_separation * (rows - 1))) / rows)

    pose_locations = [] # return val

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
            
            # For updating progress bar. To prevent being called constantly, does a little math
            new_percent = math.floor((len(pose_locations) / total_poses) * 100)
            if new_percent > curr_percent:
                curr_percent = new_percent
                # update_progress(conn, new_percent, "Preparing pose locations...", f"({len(pose_locations)}/{total_poses})")
                update_progress("update", new_percent, "Preparing pose locations...", f"({len(pose_locations)}/{total_poses})")
                # update_progress(progress_callback, new_percent, "Preparing pose locations...", f"({len(pose_locations)}/{total_poses})")
    
    # update_progress(conn, 100, f"Pose locations prepared! ({len(pose_locations)}/{len(pose_locations)})")
    return pose_locations

# Generate all-new pose data, as well as data necessary to generate images for that pose data.
# Returns pose_data and image_prep_data.
# def generate_pose_data(pose_locations, layer_data, search_data, generation_data, progress_callback = None):
# def generate_pose_data(pose_locations, layer_data, search_data, generation_data, conn = None):
def generate_pose_data(pose_locations, layer_data, search_data, generation_data):
    # update_progress(conn, 0, "Unique images found: 0")

    # stores image padding. indexes will match final image data
    # format: [(left_padding, top_padding, right_padding, bottom_padding)]
    image_prep_data = []

    # Opening layer images here so that we don't have to re-open and -close them over and over 
    layer_search_images = []
    # We don't need to do source_images yet - this is the search, after all

    # If there's a search image, add it. If not, add None just to keep indexes correct
    # (I think there's probably a more efficient way to do this, but I can't be bothered at the moment)
    for layer in layer_data:
        if layer.get("search_image_path"): 
            # layer_search_images.append(Image.open(layer["search_image_path"]))

            with Image.open(layer["search_image_path"]) as layer_image:
                layer_search_images.append(layer_image.copy()) # this should HOPEFULLY prevent the need to close these things later!
        else:
            layer_search_images.append(None)
    
    pose_data = []
    
    curr_percent = 0 # Exists to prevent near-constant calls to update_progress later on

    # Search through already-discovered poses
    for pose_index, pose_location in enumerate(pose_locations):
        # Make a box that, when Image.crop() is called, gets the correct location
        pose_box = (
            pose_location["x_position"],
            pose_location["y_position"],
            # pose_location["x_position"] + pose_location["width"] - 1,
            # pose_location["y_position"] + pose_location["height"] - 1
            pose_location["x_position"] + pose_location["width"],
            pose_location["y_position"] + pose_location["height"]
        )

        # Each pose in pose_data will have its own limb_data array
        limb_data = []

        # Search through every layer for sprites
        # TODO: At some point, make this part its own function
        for layer_index, layer in enumerate(layer_data):
            # i.e. if there's actually something we want to search here
            if layer != None and layer_search_images[layer_index] != None and not layer["is_border"] and not layer["is_cosmetic_only"]:
                # We already opened the layer images provided, so that we don't have to open and close them every time

                # update_progress("print", info_text=str(pose_index) + " " + str(layer_index))

                # Get the full image inside the pose box for this layer. "Unbound" because it still has empty space at the edges
                unbound_image = layer_search_images[layer_index].crop(pose_box)

                # The rectangle inside the image that actually contains a sprite (everything outside the bbox is just transparent pixels)
                bbox = unbound_image.getbbox()
                        
                # .getbbox() returns None if there's no sprite, so this is verifying that there's even a sprite in the first place
                if bbox:
                    # Images are cropped down to their minimum, completely-unpadded size so that comparisons to other images are much, much easier
                    bound_image = unbound_image.crop(bbox)
                            
                    # Info about images, declared outside the loop so that they persist
                    is_unique = True # Whether or not the image is a copy of another image.
                    is_flipped = False # whether the image is flipped horizontally. (Vertical flips are identical to flip_h + 180 degrees of rotation)
                    rotation_amount = 0 # Increments by 1. Each increment represents 90 degrees, up to 3 for 270

                    # Could not figure out a more efficient way to make this persist and be accurate. It works, so I'm not gonna complain.
                    image_index = 0

                    if (search_data["detect_identical_images"] or search_data["detect_rotated_images"] or
                        search_data["detect_flip_v_images"] or search_data["detect_flip_v_images"]):
                        # Checks against every single stored image, using flip_h, flip_v, & rotate. So like 12 checks per limb at worst :(
                        for image_prep in image_prep_data:
                            # Since we're not storing images, just image positions, we have to crop from the layer image. I'm not sure if it would be better
                            # to just store all of the images in memory; this seems FINE, but I'm not sure how intensive .crop() is. It's essentially just
                            # a copy, right? Is that bad? I have no idea. I was using a method where I stored the actual images before, so I could definitely
                            # switch back if necessary. The switch was made because generate_pose_data() does not need to *export* images, so I figured it
                            # didn't need to work with them as directly in general.
                            compare_to = layer_search_images[image_prep["original_layer_index"]].crop((
                                image_prep["original_pose_location"]["x_position"],
                                image_prep["original_pose_location"]["y_position"],
                                # image_prep["original_pose_location"]["width"] + image_prep["original_pose_location"]["x_position"] - 1,
                                # image_prep["original_pose_location"]["height"] + image_prep["original_pose_location"]["y_position"] - 1
                                image_prep["original_pose_location"]["width"] + image_prep["original_pose_location"]["x_position"],
                                image_prep["original_pose_location"]["height"] + image_prep["original_pose_location"]["y_position"]
                            ))
                            compare_to = compare_to.crop(compare_to.getbbox()) # Crop to bbox

                            # Compare the images: if it's unique, continue, as there's likely still images to compare against, and another later image
                            # might be identical. Once there are hundreds of unique images detected, this happens hundreds of times per layer per pose,
                            # which is why this can take a while. I'm glad it's only, like, a minute to generate overall, at least on my machine.
                            is_unique, is_flipped, rotation_amount = compare_images(
                                bound_image, compare_to,
                                search_data["detect_identical_images"], search_data["detect_rotated_images"],
                                search_data["detect_flip_h_images"], search_data["detect_flip_v_images"]
                            )

                            if not is_unique: break # If it's been detected that this image is a copy of another, no need to check for more
                            image_index += 1 # Image index is incremented here, because when I put it in other places or tried smarter methods, everything broke

                    # Padding is saved for a few reasons. Mostly, it's there to make the sprites easier to edit in a separate program once
                    # they've been output. Without the padding, there'd be no room to work with, and you'd need to increase the size of the sprites,
                    # and then everything would get cut off, and it'd just be a whole mess. Padding is also used to adjust the offsets of each limb.

                    # The same amount of custom padding is applied to all sides
                    left_padding = top_padding = right_padding = bottom_padding = generation_data["custom_padding_amount"]
                    
                    # This padding stuff can't be moved to be later even though it resembles an incoming if statement, since it still has to apply to `if is_unique`
                    if generation_data["automatic_padding_type"] != "None": 
                        left_padding += bbox[0] # The left side of the bbox perfectly matches the left padding...
                        top_padding += bbox[1] # ...same goes for the top.
                        right_padding += unbound_image.width - bbox[2] # The right- and bottom- bboxes are an x- and y-coordinate respectively, so subtracting
                        bottom_padding += unbound_image.height - bbox[3] # them from the *unbound* width gets the distance between the coordinates and max edges.

                    # Padding cannot be < 0, or images would get cut off. (I think they still CAN, if a source_image is used with bigger poses, and no padding
                    # is used whatsoever. Will try to think of a fix for that. Or maybe it simply works, I haven't checked.)
                    left_padding = max(0, left_padding)
                    top_padding = max(0, top_padding)
                    right_padding = max(0, right_padding)
                    bottom_padding = max(0, bottom_padding)

                    if is_unique: # If it's a brand-new image, its basic data needs to be added so that other images can be compared against it
                        image_prep_data.append({
                            "padding": (left_padding, top_padding, right_padding, bottom_padding),
                            "original_layer_index": layer_index, 
                            "original_pose_location": pose_location # Might eventually reformat pose_location to be (x1, y1, x2, y2) instead of (x, y, w, h)
                        })

                        # Update the pose number, so that the user knows something is actually happening
                        # update_progress(conn, None, f"Unique images found: {len(image_prep_data)}")

                    # If automatic padding is selected, EVERY pose that uses a given pose image must have their offsets adjusted to accomodate paddings that
                    # aren't even originally from their pose. In other words, padding is specific to individual pose images, but we want to make it universal instead.
                    elif generation_data["automatic_padding_type"] != "None":

                        # For consistency's sake, flip and rotate the paddings if necessary. (This is clumsy and I'm sure there's a better way,
                        # but I'm not smart enough to figure out what that'd be.)        
                        if is_flipped:
                            temp = left_padding
                            left_padding = right_padding
                            right_padding = temp

                        padding = [left_padding, top_padding, right_padding, bottom_padding]

                        # Rotate padding values counterclockwise by 90-degree steps
                        # could definitely make its own function, but then I'd have to worry about a clockwise version, and... eh
                        for _ in range(rotation_amount):
                            padding = [padding[1], padding[2], padding[3], padding[0]]

                        left_padding, top_padding, right_padding, bottom_padding = padding

                        # generation_data["automatic_padding_type"] stores a string rather than an int, simply for clarity's sake. I'm sure no one will bother
                        # reading the .json data directly, but if they did, I'd want it to be as obvious as possible what's going on.
                        match generation_data["automatic_padding_type"]: # (There's probably an even more efficient way to do this)
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
                        
                        image_prep_data[image_index]["padding"] = (left_padding, top_padding, right_padding, bottom_padding) # Update image data

                    limb = {
                        "name": layer["name"],
                        "x_offset": bbox[0], # Offsets will be edited later. At the moment, there's simply no way to know if the offsets work with the paddings,
                        "y_offset": bbox[1], # since not all images have been searched and the padding size for an image might change still.
                        "image_index": image_index,
                        "flip_h": is_flipped,
                        "rotation_amount": rotation_amount
                    }

                    limb_data.append(limb) # limb_data, a part of a single pose, has this limb appended to it

        # If the pose isn't empty, or if we *want* to generate empty poses for some reason:
        if len(limb_data) or generation_data["generate_empty_poses"]:
            pose_data.append({
                "name": f"pose_{pose_location['x_position']}_{pose_location['y_position']}",
                "x_position": pose_location["x_position"],
                "y_position": pose_location["y_position"],
                "width": pose_location["width"],
                "height": pose_location["height"],
                "limb_data": limb_data
            })
        
            new_percent = math.floor((pose_index / len(pose_locations)) * 100)
            if new_percent > curr_percent:
                curr_percent = new_percent
                # update_progress(conn, new_percent, f"Poses searched: {pose_index}/{len(pose_locations)}", f"Unique images found: {len(image_prep_data)}")
                update_progress("update", new_percent, f"Poses searched: {pose_index}/{len(pose_locations)}", f"Unique images found: {len(image_prep_data)}")
                # update_progress(progress_callback, new_percent, f"Poses searched: {pose_index}/{len(pose_locations)}", f"Unique images found: {len(image_prep_data)}")
        # update_progress(progress_callback, math.floor((pose_index / len(pose_locations) * 100)))
    
    # update_progress(conn, 100, f"Unique images found: {len(image_prep_data)}")

    # THIS is where we'll need to do a search through the limbs to change the offsets. It feels inefficient to not do it earlier, but it can't be helped.
    # (Doesn't need to happen if there's no auto padding.)
    if generation_data["automatic_padding_type"] != "None":
        for pose in pose_data:
            for limb in pose["limb_data"]:
                # Might be a better way to store this info in padding. Any good way to convert from a tuple to an array?
                left_padding, top_padding, right_padding, bottom_padding = image_prep_data[limb["image_index"]]["padding"]
                padding = [left_padding, top_padding, right_padding, bottom_padding]

                # Adjust paddings for the flip and rotation. As a bit of a side note, the offsets are saved WITH the flip and rotation in mind, but the paddings
                # are saved WITHOUT the flip and rotation in mind. There might be a better way to go about that, since it seems counterintuitive and like we need
                # to do a lot of unnecessary work, but I'm pretty sure this is the best way. Think about it - there needs to be ONE UNIVERSAL padding for a given
                # image that works for EVERY pose that uses that image, so rotation and flips shouldn't factor into that. Flip and rotation must be saved
                # *some*where, though, and the only other option is the offsets. We COULD save a left_, top_, right_, and bottom_ offset for every single limb in
                # every single pose to avoid doing this weird rotation stuff, but two of those paddings would go completely unused EVERY SINGLE time - it would
                # simply select whichever sides make sense as the left and top, given the flip and rotation of the pose. Therefore, we only NEED left_ and top_
                # saved, and since we NEED to save rotation and flip data to the offsets, the left_ and top_ padding need to undergo this process every time.
                # if limb["flip_h"]:
                #     # Flip the left and right paddings
                #     padding = [right_padding, top_padding, left_padding, bottom_padding]
                    
                #     # Rotate padding values counterclockwise by 90-degree steps
                #     # (...Gonna be honest, I don't know why we're rotating differently here? The earlier part where padding is adjusted for flips & rotation in a
                #     # similar way does not have separate methods of rotation for the flipped version. Maybe I'm doing it backwards...!)
                #     for _ in range(limb["rotation_amount"]):
                #         padding = [padding[1], padding[2], padding[3], padding[0]]
                # else: 
                #     # padding = [left_padding, top_padding, right_padding, bottom_padding]

                #     # Rotate padding values clockwise by 90-degree steps
                #     for _ in range(limb["rotation_amount"]):
                #         padding = [padding[3], padding[0], padding[1], padding[2]]

                # Rotation and flipping done in reverse order from last time, 'cause we're undoing it or something TODO make better comment

                # Rotate padding values clockwise by 90-degree steps
                for _ in range(limb["rotation_amount"]):
                    padding = [padding[3], padding[0], padding[1], padding[2]]
                
                # Flip
                if limb["flip_h"]: padding = [padding[2], padding[1], padding[0], padding[3]]

                # Offsets for each limb are adjusted by the appropriate amount.
                # I've explained this exhaustively, but not *well* - but essentially, the padding HAS to rotate whether we like it or not, so we need to
                # work around that. Will try to think of a better explanation
                limb["x_offset"] -= padding[0]
                limb["y_offset"] -= padding[1]

    # Close layer images. It's better to use the "with" keyword in general, as far as I can tell, but I don't know if there's any clean way, let alone any
    # real way at all, to use "with" when 
    # for image in layer_search_images:
    #     image.close()

    return pose_data, image_prep_data

# Generate the image data that will be exported alongside the .json, as well as the actual images that will be saved 
# def generate_image_data(image_prep_data, layer_data, pose_data, progress_callback = None): # image_data = [] is kinda clumsy
# def generate_image_data(image_prep_data, layer_data, pose_data, conn = None): # image_data = [] is kinda clumsy
def generate_image_data(image_prep_data, layer_data, pose_data): # image_data = [] is kinda clumsy
    # update_progress(conn, 0, "Generating images...")
    
    # Variable declaration
    images = []
    image_data = []
    layer_search_images = []
    layer_source_images = []

    # Used for filenames (though I guess if the filenames already exist, this isn't good? Will want to possibly think of reworking this some more
    # once I want to be able to update pose images for existing generated .jsons) Ok yeah TODO TODO TODO
    number_of_characters = len(str(len(image_prep_data)))

    curr_percent = 0

    # Store copies of layer images so we don't have to worry about opening and closing them later
    for i, layer in enumerate(layer_data):
        # If there's a search image, add it. If not, add None just to keep indexes correct
        if layer.get("search_image_path"):
            # layer_search_images.append(Image.open(layer["search_image_path"]))

            with Image.open(layer["search_image_path"]) as search_image:
                layer_search_images.append(search_image.copy())
        else:
            layer_search_images.append(None)

        # Same as above, but for source images
        if layer.get("source_image_path"):
            # layer_source_images.append(Image.open(layer["source_image_path"]))

            with Image.open(layer["source_image_path"]) as source_image:
                layer_source_images.append(source_image.copy())
        else:
            # layer_source_images.append(None)
            # done so that we don't have to worry about selecting the right thing later - we can just default to source_image
            layer_source_images.append(layer_search_images[i])
    
    # image_data = []
    for i, image_prep in enumerate(image_prep_data):
        # print("gothere")

        # if not i % 5: print(i, " got to image gen loop start")

        padding = image_prep["padding"]
        layer_index = image_prep["original_layer_index"]
        original_pose_location = image_prep["original_pose_location"]

        # The box that contains a given pose
        # (More evidence for why pose_location should probably hold an end coordinate rather than a width/height. I think we do this EVERY time.
        # will think of pros and cons, and whether we actually even USE the width and height as they are.)
        pose_box = (
            original_pose_location["x_position"],
            original_pose_location["y_position"],
            # original_pose_location["width"] + original_pose_location["x_position"] - 1,
            # original_pose_location["height"] + original_pose_location["y_position"] - 1
            original_pose_location["width"] + original_pose_location["x_position"],
            original_pose_location["height"] + original_pose_location["y_position"]
        )

        # # Get the search image, and the bound search image.
        # search_image = layer_search_images[layer_index].crop(pose_box)
        # search_image_bbox = search_image.getbbox()
        # bound_search_image = search_image.crop(search_image_bbox)

        # # Create a new image that's sized appropriately. The size is based on the SEARCH image, NOT the SOURCE image, so if we wanna avoid cutoffs this is
        # # where we'd do it.
        # padded_image = Image.new(
        #     "RGBA",
        #     ((bound_search_image.width + padding[0] + padding[2]), (bound_search_image.height + padding[1] + padding[3])),
        #     ImageColor.getrgb("#00000000") # Transparency
        # )
        
        # # # If there's no source image, the pasted image should just be the search image
        # # source_image = search_image
        # # # source_image_bbox = search_image_bbox

        # # if layer_data[layer_index].get("source_image_path"): # If there IS a source image, use it
        # #     source_image = layer_source_images[layer_index].crop(pose_box)
        # #     # source_image_bbox = source_image.getbbox()
        # #     # i feel like this might cause problems???

        # source_image = layer_source_images[layer_index].crop(pose_box)


        # # This offset is not to be confused with the stuff stored in limb_data: this is JUST for getting the art in the right place on the images themselves
        # x_offset = padding[0] - search_image_bbox[0]
        # y_offset = padding[1] - search_image_bbox[1]

        # # Finally paste the image & append it
        # padded_image.paste(source_image, (x_offset, y_offset))
        # images.append(padded_image)

        images.append(generate_image_from_layers(layer_search_images[layer_index], layer_source_images[layer_index], pose_box, padding))

        
        # if not i % 5: print(i, " got past images.append")
        
        # img = (generate_image_from_layers(layer_search_images[layer_index], layer_source_images[layer_index], pose_box, padding))
        # if img == None:
        #     raise ValueError(f"index: {i}\nimage_prep: {image_prep}")
        # images.append(img)

        # Can't store the original_pose_index in image_prep_data, since empty poses will not be stored (by default). The stored pose index would align with the
        # number of pose locations, not the actual poses that end up being saved, so they would mismatch. So, instead, we look for poses whose locations match
        # the data stored in image_prep
        original_pose_index = None

        # TODO: should maybe throw an error if it tries to find a pose that doesn't exist
        # Also I'm not sure why this works fine here, but it didn't work well for image_index back in generate_pose_data()?
        for original_pose_index, pose in enumerate(pose_data):
            if pose["x_position"] == original_pose_location["x_position"] and pose["y_position"] == original_pose_location["y_position"]:
                break
        
        # if not i % 5: print(i, " got past original_pose_index loop")
        
        # If there's already appropriate image data, use that instead. We'll probably want to split generate_image_data into a few different functions for
        # the different possibilities, honestly. I dunno.
        image_data.append({
            "path": f"{str(i).rjust(number_of_characters, '0')}.png",
            "original_pose_index": original_pose_index,
            "original_layer_index": image_prep["original_layer_index"]
        })

        
        # if not i % 5: print(i, " got past image_data.append")

        # update_progress(conn, , "Generating images...")
        new_percent = math.floor((len(images) / len(image_prep_data)) * 100)
        if new_percent > curr_percent:
            curr_percent = new_percent
            # update_progress(conn, new_percent, "Generating images..." + f"({len(images)})")
            update_progress("update", new_percent, "Generating images..." + f"({len(images)})")
            # update_progress(progress_callback, new_percent, "Generating images..." + f"({len(images)})")

        
        # if not i % 5: print(i, " got to end of image gen loop")

    # update_progress(conn, 100, f"Images generated: {len(image_prep_data)}")
    
    # print("got to generate_image_data return")
    return image_data, images

def generate_image_from_layers(original_layer_image, source_layer_image, pose_box, padding):
    # source_image = source_layer_image.crop(pose_box)
    # source_bbox = source_image.getbbox()
    # bound_source_image = source_image.crop(source_bbox)

    original_image = original_layer_image.crop(pose_box)
    original_bbox = original_image.getbbox()
    bound_original_image = original_image.crop(original_bbox)

    offset = (padding[0] - original_bbox[0], padding[1] - original_bbox[1])

    return generate_image(
        source_layer_image.crop(pose_box),
        ((bound_original_image.width + padding[0] + padding[2]), (bound_original_image.height + padding[1] + padding[3])),
        offset
    )

# def update_existing_image(existing_layer_image, new_layer_image, pose_box):
#     pass

def generate_image(input_image, size, offset):
    # return Image.new("RGBA", size, ImageColor.getrgb("#00000000")).paste(input_image, offset)
    image = Image.new(
        "RGBA", size,
        ImageColor.getrgb("#00000000") # Transparency
    )

    image.paste(input_image, offset)

    return image

# def generate_layer_data(input_layer_data, output_folder_path, paths_are_local):
def generate_layer_data(input_layer_data):
    output_layer_data = []
    search_images = []
    source_images = []
    
    for layer in input_layer_data:
        search_image_path = None
        source_image_path = None

        # if layer["export_original_images"]: # i MIGHT like this name more??? idk
        if layer["export_layer_images"]:

            if layer["search_image_path"]:
                # search_image_path = (
                #     (f"{layer['name']}_" + ("search" if layer["source_image_path"] else "layer") + "_image.png") # i kinda like the _layer_image.png naming idea TODO TODO TODO TODO yeah do this honestly
                #     if not layer["is_border"] else
                #     "border.png"
                # )
                search_image_path = (
                    (f"{layer['name']}" + ("" if layer["is_cosmetic_only"] else "_search") + "_image.png")
                    if not layer["is_border"] else
                    "border_image.png"
                )

                with Image.open(layer["search_image_path"]) as search_image:
                    # search_image.save(output_folder_path + search_image_path)
                    search_images.append(search_image.copy())

                # if not paths_are_local: search_image_path = output_folder_path + search_image_path
                # if not paths_are_local: search_image_path = output_folder_path + "/" + search_image_path
                # if not paths_are_local: search_image_path = os.path.join(output_folder_path, search_image_path)
            else:
                search_images.append(None)
            if layer["source_image_path"]:
                source_image_path = f"{layer['name']}_source_image.png"

                with Image.open(layer["source_image_path"]) as source_image:
                    # source_image.save(output_folder_path + source_image_path)
                    source_images.append(source_image.copy())

                # if not paths_are_local: source_image_path = output_folder_path + source_image_path
                # if not paths_are_local: source_image_path = output_folder_path + "/" + source_image_path
                # if not paths_are_local: source_image_path = os.path.join(output_folder_path, source_image_path) # do we NEED this? paths_are_local has basically nothing to do with generation, right? it's only saving layerselect data to folder?
            else:
                source_images.append(None)

        output_layer_data.append({
            "name": layer["name"],
            "search_image_path": (os.path.basename(search_image_path) if search_image_path else None),
            "source_image_path": (os.path.basename(source_image_path) if source_image_path else None),
            # "is_border": layer["is_border"], "is_cosmetic_only": layer["is_cosmetic_only"], "export_layer_images": layer.get("export_layer_images")
            "is_border": layer.get("is_border") == True, "is_cosmetic_only": layer.get("is_cosmetic_only") == True,
            "export_layer_images": layer.get("export_layer_images") == True
        })

    return output_layer_data, search_images, source_images

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