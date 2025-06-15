import math
import os
import json

from PIL import Image, ImageColor
from itertools import chain

from shared import consistxels_version

# Output progress to main process
def update_progress(type="update", value = None, header_text = None, info_text = None):
    update = {"type": type, "value": value, "header_text": header_text, "info_text": info_text}
    print(json.dumps(update), flush=True)

# Generate and save a full .json output file, and save all generated pose images
def generate_all_pose_data(input_data, output_folder_path): #input_data is already in proper structure for consistxels .json
    try:
        # Do we really need this? I dunno
        output_dir = os.path.abspath(output_folder_path)
        os.makedirs(output_dir, exist_ok=True) # I mean, this is NICE to have, tho

        # Variable declaration

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
            size = img.size

        # Match the search type
        match search_type_data["search_type"]:
            case "Border":
                pose_locations = search_border(search_data, search_type_data, input_layer_data)
            case "Spacing":
                pose_locations = search_spacing(search_data, search_type_data, size) # TODO: Test
            case "Preset":
                pose_locations = input_pose_data # TODO: Test
            case _:
                pass # TODO: throw exception: invalid search type

        # Output pose data. Also output some image data; I would have liked to separate them, but they're so conceptually intertwined that I don't think it's possible
        output_pose_data, image_prep_data = generate_pose_data(pose_locations, input_layer_data, search_data, generation_data)

        # Using the pose and image_prep data, generate the final output image_data as well as the actual images
        image_data, images = generate_image_data(image_prep_data, input_layer_data, output_pose_data)

        update_progress("update", 100, "", "Wrapping up...")
        
        # Save pose images
        # TODO: May want to think of better way to do this. Definitely works for now, though
        for i in range(len(images)):
            image_path = os.path.join(output_dir, image_data[i]["path"])
            images[i].save(image_path)

        # Save OUTPUT layer data, useful if any layers are cosmetic-only or a border
        output_layer_data, search_images, source_images = generate_layer_data(input_layer_data)

        # TODO: test. not sure if the method below this one had anything over something like this. maybe i was just tired??
        for i, layer in enumerate(output_layer_data):
            if layer.get("export_layer_images"):
                if search_images[i]:
                    image_path = output_layer_data[i]["search_image_path"]
                    search_images[i].save(os.path.join(output_dir, image_path))
                if source_images[i]:
                    image_path = output_layer_data[i]["source_image_path"]
                    source_images[i].save(os.path.join(output_dir, image_path))

        # for i in range(len(search_images)):
        #     # print("saving image", i)
        #     # images[i].save(output_folder_path + image_data[i]["path"])
        #     if search_images[i]:
                
        #         image_path = output_layer_data[i]["search_image_path"]
        #         # if input_header["paths_are_local"]: image_path = os.path.join(output_dir, output_layer_data[i]["search_image_path"])
                
        #         # search_images[i].save(image_path)
        #         search_images[i].save(os.path.join(output_dir, image_path))

        # for i in range(len(source_images)):
        #     # print("saving image", i)
        #     # images[i].save(output_folder_path + image_data[i]["path"])
        #     if source_images[i]:
                
        #         image_path = output_layer_data[i]["source_image_path"]
        #         # if input_header["paths_are_local"]: image_path = os.path.join(output_dir, output_layer_data[i]["source_image_path"])
                
        #         # source_images[i].save(image_path)
        #         source_images[i].save(os.path.join(output_dir, image_path))

        # Structure output
        output_header = {
            "name": input_header["name"],
            "consistxels_version": consistxels_version,
            # "paths_are_local": input_header["paths_are_local"],
            "paths_are_local": True, # Paths are DEFINITELY local here, no matter whether the input's paths were local
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

        # Prep to save json
        json_filename = "consistxels_pose_output_" + output_header["name"] + ".json"
        json_path = os.path.join(output_dir, json_filename)

        # Save json
        with open(json_path, 'w') as file:
            json.dump(output_data, file, indent=4)

    except Exception as e:
        update_progress("error", 0, "An error occured", str(e))

# Gets passed layer_data and finds the border; uses said border to find and return pose locations.
# Could DEFINITELY just pass ONE layer - just the border, we don't need any other layers necessarily.
# TODO: Make work for irregular pose box sizes. Would take longer (though possibly not significantly longer), so make it optional
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

        # Get color that will be treated as border edge (formatted for Image library, and made opaque)
        # TODO: test if values that already have alpha can make it here, and stop 'em. probably throw error too
        border_color_rgb = ImageColor.getrgb(search_type_data["border_color"] + "ff")

        # TODO errors if these don't exist, I guess??
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
                        found_pose_width = endborder_x - x - 1
                        found_pose_height = endborder_y - y - 1

                        # Pose location appended as object, to fit with formatting of other search types (pose locations are essentially the same
                        # structure as .json pose_data, just with less info)
                        pose_locations.append({
                            "x_position": found_pose_x,
                            "y_position": found_pose_y,
                            "width": found_pose_width,
                            "height": found_pose_height,
                        })
            
            # For updating progress bar. To prevent being called constantly, does a little math
            new_percent = math.floor((y / (height - 2)) * 100)
            if new_percent > curr_percent:
                curr_percent = new_percent
                update_progress("update", new_percent, "Searching border image for valid pose boxes...", f"(Pose boxes found: {len(pose_locations)})")

    # List of pose objects is returned
    return pose_locations

# Get a list of pose locations from the provided search_data and size
def search_spacing(search_data, search_type_data, size):
    # Prepare variables
    rows = search_type_data["spacing_rows"]
    columns = search_type_data["spacing_columns"]
    total_poses = rows * columns # For showing progress
    
    curr_percent = 0 # Exists to prevent near-constant calls to update_progress later on

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
                update_progress("update", new_percent, "Preparing pose locations...", f"({len(pose_locations)}/{total_poses})")
    
    return pose_locations

# Generate all-new pose data, as well as data necessary to generate images for that pose data.
# Returns pose_data and image_prep_data.
# TODO: think of renaming? shares name with the general concept, and some other functions that EVENTUALLY lead to this one but idk idk idk idk TODO rewrite this comment
def generate_pose_data(pose_locations, layer_data, search_data, generation_data):

    # Stores image padding. indexes will match final image data
    # Format: [(left_padding, top_padding, right_padding, bottom_padding)]
    image_prep_data = []

    # Opening layer images here so that we don't have to re-open and -close them over and over 
    layer_search_images = []
    # We don't need to do source_images yet - this is the search, after all

    # If there's a search image, add it. If not, add None just to keep indexes correct
    # (I think there's probably a more efficient way to do this, but I can't be bothered at the moment)
    for layer in layer_data:
        if layer.get("search_image_path"): 

            with Image.open(layer["search_image_path"]) as layer_image:
                layer_search_images.append(layer_image.copy()) # Prevents needing to close these images later
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

            # Update progress        
            new_percent = math.floor((pose_index / len(pose_locations)) * 100)
            if new_percent > curr_percent:
                curr_percent = new_percent
                update_progress("update", new_percent, f"Poses searched: {pose_index}/{len(pose_locations)}", f"Unique images found: {len(image_prep_data)}")
                
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
                
                # TODO: re-read and probably rewrite the above comment. I need to get better at explaining things quickly and intuitively

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

    return pose_data, image_prep_data

# Generate the image data that will be exported alongside the .json, as well as the actual images that will be saved
def generate_image_data(image_prep_data, layer_data, pose_data):
    
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
            with Image.open(layer["search_image_path"]) as search_image:
                layer_search_images.append(search_image.copy())
        else:
            layer_search_images.append(None)

        # Same as above, but for source images
        if layer.get("source_image_path"):
            with Image.open(layer["source_image_path"]) as source_image:
                layer_source_images.append(source_image.copy())
        else:
            # done so that we don't have to worry about selecting the right thing later - we can just default to source_image
            layer_source_images.append(layer_search_images[i])
    
    for i, image_prep in enumerate(image_prep_data):

        padding = image_prep["padding"]
        layer_index = image_prep["original_layer_index"]
        original_pose_location = image_prep["original_pose_location"]

        # The box that contains a given pose
        # (More evidence for why pose_location should probably hold an end coordinate rather than a width/height. I think we do this EVERY time.
        # will think of pros and cons, and whether we actually even USE the width and height as they are.)
        pose_box = (
            original_pose_location["x_position"],
            original_pose_location["y_position"],
            original_pose_location["width"] + original_pose_location["x_position"],
            original_pose_location["height"] + original_pose_location["y_position"]
        )

        images.append(generate_image_from_layers(layer_search_images[layer_index], layer_source_images[layer_index], pose_box, padding))

        # Can't store the original_pose_index in image_prep_data, since empty poses will not be stored (by default). The stored pose index would align with the
        # number of pose locations, not the actual poses that end up being saved, so they would mismatch. So, instead, we look for poses whose locations match
        # the data stored in image_prep
        original_pose_index = None

        # TODO: should maybe throw an error if it tries to find a pose that doesn't exist
        # Also I'm not sure why this works fine here, but it didn't work well for image_index back in generate_pose_data()?
        for original_pose_index, pose in enumerate(pose_data):
            if pose["x_position"] == original_pose_location["x_position"] and pose["y_position"] == original_pose_location["y_position"]:
                break
        
        # If there's already appropriate image data, use that instead. We'll probably want to split generate_image_data into a few different functions for
        # the different possibilities, honestly. I dunno.
        image_data.append({
            "path": f"{str(i).rjust(number_of_characters, '0')}.png",
            "original_pose_index": original_pose_index,
            "original_layer_index": image_prep["original_layer_index"]
        })

        new_percent = math.floor((len(images) / len(image_prep_data)) * 100)
        if new_percent > curr_percent:
            curr_percent = new_percent
            update_progress("update", new_percent, "Generating images..." + f"({len(images)})")

    return image_data, images

def generate_image_from_layers(original_layer_image, source_layer_image, pose_box, padding):

    original_image = original_layer_image.crop(pose_box)
    original_bbox = original_image.getbbox()
    bound_original_image = original_image.crop(original_bbox)

    offset = (padding[0] - original_bbox[0], padding[1] - original_bbox[1])
    size = ((bound_original_image.width + padding[0] + padding[2]), (bound_original_image.height + padding[1] + padding[3]))

    # return generate_image(
    #     source_layer_image.crop(pose_box),
    #     ((bound_original_image.width + padding[0] + padding[2]), (bound_original_image.height + padding[1] + padding[3])),
    #     offset
    # )
    return generate_image_from_source_layer(source_layer_image, pose_box, size, offset)

def generate_image_from_source_layer(source_layer_image, pose_box, size, offset):
    return generate_image(source_layer_image.crop(pose_box), size, offset)

def generate_image(input_image, size, offset):
    image = Image.new(
        "RGBA", size,
        ImageColor.getrgb("#00000000") # Transparency
    )

    image.paste(input_image, offset)

    return image

def generate_layer_data(input_layer_data):
    output_layer_data = []
    search_images = []
    source_images = []
    
    for layer in input_layer_data:
        search_image_path = None
        source_image_path = None

        if layer["export_layer_images"]:

            if layer["search_image_path"]:
                search_image_path = (
                    (f"{layer['name']}" + ("" if layer["is_cosmetic_only"] else "_search") + "_image.png")
                    if not layer["is_border"] else
                    "border_image.png"
                )

                with Image.open(layer["search_image_path"]) as search_image:
                    search_images.append(search_image.copy())

            else:
                search_images.append(None)
            if layer["source_image_path"]:
                source_image_path = f"{layer['name']}_source_image.png"

                with Image.open(layer["source_image_path"]) as source_image:
                    source_images.append(source_image.copy())

            else:
                source_images.append(None)

        output_layer_data.append({
            "name": layer["name"],
            "search_image_path": (os.path.basename(search_image_path) if search_image_path else None),
            "source_image_path": (os.path.basename(source_image_path) if source_image_path else None),
            "is_border": layer.get("is_border") == True, "is_cosmetic_only": layer.get("is_cosmetic_only") == True,
            "export_layer_images": layer.get("export_layer_images") == True
        })

    return output_layer_data, search_images, source_images

# Return vals: is_unique, is_flipped, rotation_amount
def compare_images(image:Image, compare_to:Image, detect_identical_images = True, detect_rotated_images = True, detect_flip_h_images = True, detect_flip_v_images = False):
    if detect_identical_images and image.tobytes() == compare_to.tobytes(): # the image is already stored; move on
        return False, False, 0

    # a necessary evil, i think
    flip_h = None

    if detect_flip_h_images:
        # prepare a flipped version of the img, since it'll commonly be an already-stored img, and it's in a lotta checks
        flip_h = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        if flip_h.tobytes() == compare_to.tobytes(): # the flipped image is already stored; move on
            return False, True, 0

    if detect_rotated_images:                    
        # rotate normal image 90 degrees
        if image.transpose(Image.Transpose.ROTATE_90).tobytes() == compare_to.tobytes():
            return False, False, 1

        # rotate normal image 180 degrees
        if image.transpose(Image.Transpose.ROTATE_180).tobytes() == compare_to.tobytes():
            return False, False, 2

        # rotate normal image 270 degrees
        if image.transpose(Image.Transpose.ROTATE_270).tobytes() == compare_to.tobytes():
            return False, False, 3

    if detect_flip_h_images and detect_rotated_images:
        # rotate flipped image 270 degrees (i.e. -90 degrees, 'cause it's flipped)
        if flip_h.transpose(Image.Transpose.ROTATE_270).tobytes() == compare_to.tobytes():
            return False, True, 3

        # rotate flipped image 180 degrees
        if flip_h.transpose(Image.Transpose.ROTATE_180).tobytes() == compare_to.tobytes():
            return False, True, 2

        # rotate flipped image 90 degrees (i.e. -270 degrees, 'cause it's flipped)
        if flip_h.transpose(Image.Transpose.ROTATE_90).tobytes() == compare_to.tobytes():
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
    
    # Getting here doesn't mean the image IS unique OVERALL - it still likely has to check against many more images
    return True, False, 0

def generate_sheet_image(selected_layers, data, input_folder_path, output_folder_path):
    size = (data["header"]["width"], data["header"]["height"])
    layer_images = place_pose_images(data["image_data"], generate_image_placement_data(selected_layers, False, data["pose_data"], data["layer_data"], data["image_data"]), data["layer_data"], size, input_folder_path)

    color_transparent = ImageColor.getrgb("#00000000")
    sheet_image = Image.new("RGBA", size, color_transparent)

    for i, layer_image in enumerate(layer_images): # probably a better way to do this
        if not i in selected_layers: layer_images.pop(i)

    for layer_image in reversed(layer_images):
        sheet_image.alpha_composite(layer_image)

    # need to ask if want to overwrite somewhere
    # ALSO output_folder_path is not necessarily the same as the INPUT folder path! might as well separate them in case someone wants to export to a location other than the one the pose images are. otherwise, what's even the point of having an option to enter an output path?
    sheet_image.save(os.path.join(output_folder_path, f"export_{data["header"]["name"]}_sheet.png"))

def generate_layer_images(selected_layers, unique_only, data, input_folder_path, output_folder_path):
    size = (data["header"]["width"], data["header"]["height"])
    layer_images = place_pose_images(data["image_data"], generate_image_placement_data(selected_layers, unique_only, data["pose_data"], data["layer_data"], data["image_data"]), data["layer_data"], size, input_folder_path)

    for i, layer_image in enumerate(layer_images):
        if i in selected_layers:
            path = (f"export_{data["header"]["name"]}_layer_{data["layer_data"][i]["name"]}.png") # COULD have filetype be selectable? though i have no idea why anyone would use anything other than png
            layer_image.save(os.path.join(output_folder_path, path))

def generate_external_filetype(selected_layers, unique_only, data, input_folder_path, output_folder_path):
    pass

def generate_image_placement_data(selected_layers, unique_only, pose_data, layer_data, image_data):
    layer_names = [layer.get("name") for layer in layer_data]

    image_placement_data = []
    for _ in range(len(image_data)):
        image_placement_data.append([])

    for pose_index, pose in enumerate(pose_data):
        x_position = pose["x_position"]
        y_position = pose["y_position"]

        limb_data = pose["limb_data"]
        for limb in limb_data:
            layer_index = layer_names.index(limb["name"])
            if layer_index in selected_layers:

                x_offset = limb["x_offset"]
                y_offset = limb["y_offset"]

                image_index = limb["image_index"]

                if (not unique_only) or (image_data[image_index]["original_pose_index"] == pose_index):
                    image_placement_data[image_index].append({"x_position": x_position + x_offset, "y_position": y_position + y_offset, "layer_index": layer_index, "flip_h": limb["flip_h"], "rotation_amount": limb["rotation_amount"]})

    # dawning on me that we can check for original pose index if we simply look through pose data for the first instance. we're kinda doing that anyway. think abt this
    return image_placement_data

def place_pose_images(image_data, image_placement_data, layer_data, size, input_folder_path):

    layer_images = [None] * len(layer_data)
    color_transparent = ImageColor.getrgb("#00000000")

    img_base = Image.new("RGBA", size, color_transparent)

    for i, layer in enumerate(layer_data):
        if layer["is_border"] or layer["is_cosmetic_only"]:
            # if paths are local (which they usually will be):
            path = os.path.join(input_folder_path, layer["search_image_path"])
            with Image.open(path) as image:
                layer_images[i] = image.copy()
        else:
            layer_images[i] = img_base.copy()
    
    for i, image_placement in enumerate(image_placement_data):
        with Image.open(os.path.join(input_folder_path, image_data[i]["path"])) as image:
            
            for limb_placement in image_placement:
                if limb_placement != None and layer_images[limb_placement["layer_index"]] != None:
                    adjusted_image = image.copy()

                    match limb_placement["rotation_amount"]:
                        case 1:
                            adjusted_image = adjusted_image.transpose(Image.Transpose.ROTATE_270)
                        case 2:
                            adjusted_image = adjusted_image.transpose(Image.Transpose.ROTATE_180)
                        case 3:
                            adjusted_image = adjusted_image.transpose(Image.Transpose.ROTATE_90)
                    
                    if limb_placement["flip_h"]: adjusted_image = adjusted_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

                    layer_images[limb_placement["layer_index"]].paste(adjusted_image, (limb_placement["x_position"], limb_placement["y_position"]))

    return layer_images
    
# updated_layers in format [{"new_image_path"}, {...}...] or something to that effect
def generate_updated_pose_images(new_image_paths, data, input_folder_path):
    # get original pose bbox
    # get img from new_image_path layer image inside original pose bbox (per layer)
    # paste new img onto old one, or clear old one, or something

    layer_names = [layer.get("name") for layer in data["layer_data"]] # so we WILL need to EITHER prevent identical layer names, OR fill pose limb_data with empty limbs for each unused layer. (OR!!!! store layer_index in limb_data, rather than the layer's name. we can still store the name, but ALSO the layer index - i like this plan best)

    new_layer_images = [None] * len(new_image_paths)
    for i, new_image_path in enumerate(new_image_paths):
        if new_image_path:
            with Image.open(new_image_path) as new_layer_image:
                new_layer_images[i] = new_layer_image.copy()

    for image_datum in data["image_data"]:

        layer_index = image_datum["original_layer_index"]
        if new_layer_images[layer_index] != None:

            pose = data["pose_data"][image_datum["original_pose_index"]]
            pose_box = (pose["x_position"], pose["y_position"], pose["x_position"] + pose["width"], pose["y_position"] + pose["height"])

            limb = next(l for l in pose["limb_data"] if l["name"] == layer_names[image_datum["original_layer_index"]])

            with Image.open(os.path.join(input_folder_path, image_datum["path"])) as image:
                size = image.size
                
            offset = (-limb["x_offset"], -limb["y_offset"])

            generate_image_from_source_layer(
                new_layer_images[image_datum["original_layer_index"]], pose_box, size, offset
            ).save(os.path.join(input_folder_path, image_datum["path"]))

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
            return chain(right_range, left_range) # Will iterate rightward from center, then leftward from center
        else:
            return chain(left_range, right_range) # Will iterate leftward from center, then rightward from center
    else:
        if not search_right_to_left:
            return range(start, end + edge_offset) # Will iterate righward from leftmost edge
        else:
            return range(end + edge_offset - 1, start - 1, -1) # Will iterate leftward from rightmost edge