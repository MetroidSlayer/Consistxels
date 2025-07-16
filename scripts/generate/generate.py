import math
import os
import json
import numpy
import traceback

from PIL import Image, ImageColor
from itertools import chain

from scripts.shared import consistxels_version

import aseprite_file

import psapi # https://github.com/EmilDohne/PhotoshopAPI/tree/master

# Output progress to main process
def update_progress(type="update", value = None, header_text = None, info_text = None):
    update = {"type": type, "value": value, "header_text": header_text, "info_text": info_text}
    print(json.dumps(update), flush=True)

# Generate and save a full .json output file, and save all generated pose images
def generate_sheet_data(input_data, output_folder_path): #input_data is already in proper structure for consistxels .json
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
        size = (0,0)
        layer = next(layer for layer in input_layer_data if (layer.get("search_image_path") or layer.get("source_image_path")))
        with Image.open(layer["search_image_path"] if layer.get("search_image_path") else layer["source_image_path"]) as img:
            size = img.size
        
        if size[0] <= 0 or size[1] <= 0:
            print(json.dumps({"type":"error", "value":0, "info_text":"Image has invalid height or width"}))
            raise ValueError

        # Match the search type
        match search_type_data["search_type"]:
            case "Border":
                pose_locations = search_border(search_data, search_type_data, input_layer_data)
            case "Spacing":
                pose_locations = search_spacing(search_data, search_type_data, size)
            case "Preset":
                pose_locations = input_pose_data
            case _:
                print(json.dumps({"type":"error", "value":0, "info_text":f"{search_type_data["search_type"]} is not a valid search type"}))
                raise ValueError # handle this better by putting error message in valueerror?

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

        # Save search and source images, if they exist and should be saved
        for i, layer in enumerate(output_layer_data):
            if layer.get("export_layer_images"):
                if search_images[i]:
                    image_path = output_layer_data[i]["search_image_path"]
                    search_images[i].save(os.path.join(output_dir, image_path))
                if source_images[i]:
                    image_path = output_layer_data[i]["source_image_path"]
                    source_images[i].save(os.path.join(output_dir, image_path))

        # Structure output
        output_header = {
            "name": input_header["name"],
            "consistxels_version": consistxels_version,
            "type": "sheetdata_generated",
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
        json_filename = "consistxels_sheet_data_" + output_header["name"] + ".json"
        json_path = os.path.join(output_dir, json_filename)

        # Save json
        with open(json_path, 'w') as file:
            json.dump(output_data, file, indent=4)

    except Exception as e:
        update_progress("error", 0, "An error occurred", traceback.format_exc()) # MAYBE this will work???

# Gets passed layer_data and finds the border; uses said border to find and return pose locations.
# Could DEFINITELY just pass ONE layer - just the border, we don't need any other layers necessarily.
# TODO: Make work for irregular pose box sizes. Would take longer (though possibly not significantly longer), so make it optional
def search_border(search_data, search_type_data, layer_data):
    # Determine which layer is the border
    border_layer = next(layer for layer in layer_data if layer.get("is_border"))
    # TODO: throw exception if border_layer == None # I mean... we don't HAVE to? An exception will be raised automatically if it attempts to open an image that's None

    # Open the border image
    with Image.open(border_layer["search_image_path"]) as border_image:
        # Get image size (technically, we could take it from earlier, but I'd like this to operate on its own)
        width, height = border_image.size

        curr_percent = 0 # Exists to prevent near-constant calls to update_progress later on

        # Get color that will be treated as border edge (formatted for Image library, and made opaque)
        # TODO: test if values that already have alpha can make it here, and stop 'em. probably throw error too
        border_color_rgb = ImageColor.getrgb(search_type_data["border_color"] + "ff")

        start_search_in_center = search_data.get("start_search_in_center", True)
        search_right_to_left = search_data.get("search_right_to_left", False)

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
    for grid_y in range(rows):
        for grid_x in get_x_range(0, columns, start_search_in_center, search_right_to_left, 0):
            # Essentially, we're trying to find the top-left corner of every pose box.
            # Outer padding applies exactly once to all top-left corners of pose boxes, no matter what
            # Inner padding applies at least once, plus twice per previous pose box
            # Sprite height/width and x/y separation apply only for sprites that have already been counted

            pose_locations.append({
                "x_position": outer_padding + inner_padding + (((inner_padding * 2) + sprite_width + x_separation) * grid_x),
                "y_position": outer_padding + inner_padding + (((inner_padding * 2) + sprite_height + y_separation) * grid_y),
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
def generate_pose_data(pose_locations, layer_data, search_data, generation_data):
    detect_identical_images = search_data["detect_identical_images"]
    detect_rotated_images = search_data["detect_rotated_images"]
    detect_flip_h_images = search_data["detect_flip_h_images"]
    detect_flip_v_images = search_data["detect_flip_v_images"]

    # Stores image padding. indexes will match final image data
    # Format: [(left_padding, top_padding, right_padding, bottom_padding)]
    image_prep_data = []

    # Store some info about images for comparisons. These remain empty if no detect types are selected
    image_bytes_data : list[bytes] = []
    image_bound_sizes_data : list[tuple[int, int]] = []

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
        # TODO: At some point, make this part its own function # NOT sure what I meant by "this part". Just the layer search? I dunno, would that ever be used elsewhere? I agree in theory but it might not be worth it
        for layer_index, layer in enumerate(layer_data):
            # i.e. if there's actually something we want to search here
            if layer != None and layer_search_images[layer_index] != None and not layer["is_border"] and not layer["is_cosmetic_only"]:
                # We already opened the layer images provided, so that we don't have to open and close them every time

                # Get the full image inside the pose box for this layer. "Unbound" because it still has empty space at the edges
                unbound_image : Image.Image = layer_search_images[layer_index].crop(pose_box)

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

                    # If any detect types are selected:
                    if (detect_identical_images or detect_rotated_images or
                        detect_flip_h_images or detect_flip_v_images):

                        # Could probably move this stuff into its own function, so as to not clog up generate_pose_data(), but whatever I can do that later

                        # Initialize a new list for this image's variation's bytes and sizes
                        curr_image_bytes_set : list[bytes] = [None] * 9
                        curr_image_sizes_set : list[tuple[int, int]] = [None] * 9
                        
                        # Unmodified image
                        if detect_identical_images:
                            curr_image_bytes_set[0] = bound_image.tobytes()
                            curr_image_sizes_set[0] = bound_image.size                        

                        # Horizontally-flipped image
                        if detect_flip_h_images:
                            flip_h_image = bound_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                            curr_image_bytes_set[1] = flip_h_image.tobytes()
                            curr_image_sizes_set[1] = flip_h_image.size

                            # Flipped & rotated images (it makes more intuitive sense to do them later, but this way we don't have to re-transpose flip_h)
                            if detect_rotated_images:
                                # Flipped & rotated 90 degrees (i.e. -270 degrees, I think)
                                flip_h_rot90_image = flip_h_image.transpose(Image.Transpose.ROTATE_90)
                                curr_image_bytes_set[5] = flip_h_rot90_image.tobytes()
                                curr_image_sizes_set[5] = flip_h_rot90_image.size
                                
                                # Flipped & rotated 180 degrees
                                flip_h_rot180_image = flip_h_image.transpose(Image.Transpose.ROTATE_180)
                                curr_image_bytes_set[6] = flip_h_rot180_image.tobytes()
                                curr_image_sizes_set[6] = flip_h_rot180_image.size
                                
                                # Flipped & rotated 270 degrees
                                flip_h_rot270_image = flip_h_image.transpose(Image.Transpose.ROTATE_270)
                                curr_image_bytes_set[7] = flip_h_rot270_image.tobytes()
                                curr_image_sizes_set[7] = flip_h_rot270_image.size

                        # Rotated images
                        if detect_rotated_images:
                            # Rotated 90 degrees
                            rot90_image = bound_image.transpose(Image.Transpose.ROTATE_90)
                            curr_image_bytes_set[2] = rot90_image.tobytes()
                            curr_image_sizes_set[2] = rot90_image.size
                            
                            # Rotated 180 degrees
                            rot180_image = bound_image.transpose(Image.Transpose.ROTATE_180)
                            curr_image_bytes_set[3] = rot180_image.tobytes()
                            curr_image_sizes_set[3] = rot180_image.size
                            
                            # Rotated 270 degrees
                            rot270_image = bound_image.transpose(Image.Transpose.ROTATE_270)
                            curr_image_bytes_set[4] = rot270_image.tobytes()
                            curr_image_sizes_set[4] = rot270_image.size

                        # Vertically-flipped image
                        # (it's an elif because you can't select detect_rotated and detect_flip_v at the same time, since a flip_v image is
                        # the same as flipped horizontally and rotated 180 degrees)
                        elif detect_flip_v_images:
                            flip_v_image = bound_image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                            curr_image_bytes_set[8] = flip_v_image.tobytes()
                            curr_image_sizes_set[8] = flip_v_image.size

                        # Checks against every single stored image, using stored byte and size info. 8 checks per limb at worst.
                        for stored_image_index in range(len(image_bytes_data)):
                            # Compare the images: if it's unique, continue, as there's likely still images to compare against, and another later image
                            # might be identical. Once there are hundreds of unique images detected, this happens hundreds of times per layer per pose.
                            # AS OF THE NEWEST IMPLEMENTATION, this is basically instant??? WHY is it so fast.
                            is_unique, is_flipped, rotation_amount = compare_images(
                                curr_image_bytes_set, curr_image_sizes_set, image_bytes_data[stored_image_index], image_bound_sizes_data[stored_image_index]
                            )

                            if not is_unique: break # If it's been detected that this image is a copy of another, no need to check for more
                            image_index += 1 # Image index is incremented here, because when I put it in other places or tried smarter methods, everything broke
                        
                        # If it's unique, add these bytes & size to list, to be compared against later. Not added alongside other is_unique stuff, as this
                        # only needs to happen if any detect types are selected, and this is still in-scope for that one if statement up there
                        if is_unique:
                            image_bytes_data.append(curr_image_bytes_set[0])
                            image_bound_sizes_data.append(curr_image_sizes_set[0])

                    # Save padding - i.e., the space between the bound search image and the edge of the output pose image on a given side. Padding is
                    # saved such that it's consistent, no matter what the flip or rotation of the image is; therefore, when calculating offsets later,
                    # flip and rotation must be accounted for.
                    #
                    # Padding is saved for a few reasons. Mostly, it's there to make the sprites easier to edit in a separate program once
                    # they've been output. Without the padding, there'd be no room to work with, and you'd need to increase the size of the sprites,
                    # and then everything would get cut off, and it'd just be a whole mess.

                    # The same amount of custom padding is applied to all sides
                    left_padding = top_padding = right_padding = bottom_padding = generation_data["custom_padding_amount"]
                    
                    # This padding stuff can't be moved to be later even though it resembles an incoming if statement, since it still has to apply to `if is_unique`
                    if generation_data["automatic_padding_type"] != "None": 
                        left_padding += bbox[0] # The left side of the bbox perfectly matches the left padding...
                        top_padding += bbox[1] # ...same goes for the top.
                        right_padding += unbound_image.width - bbox[2] # The right- and bottom- bboxes are an x- and y-coordinate respectively, so subtracting
                        bottom_padding += unbound_image.height - bbox[3] # them from the *unbound* width gets the distance between the coordinates and max edges.

                    # Padding cannot be < 0, or images would get cut off. (I think they still CAN, if a source_image is used that has bigger images, and no padding
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
                        "layer_index": layer_index,
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

        # For updating progress bar. To prevent being called constantly, does a little math
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

                # Adjust paddings to account for flip and rotation, then apply the paddings to the offset. It might seem a bit counterintuitive to calculate
                # and undo the padding flip/rotation a few times, but this way we make sure we're ONLY saving the sides that are actually being used on a
                # per-limb basis.  

                # Rotation and flipping done in reverse order from last time, because we're effectively undoing the calculations from earlier (I think?).

                # Rotate padding values clockwise by 90-degree steps
                for _ in range(limb["rotation_amount"]):
                    padding = [padding[3], padding[0], padding[1], padding[2]]
                
                # Flip
                if limb["flip_h"]: padding = [padding[2], padding[1], padding[0], padding[3]]

                # Offsets for each limb are adjusted by the appropriate amount.
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

    # Used for filenames
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

        # Also I'm not sure why this works fine here, but it didn't work well for image_index back in generate_pose_data()?
        for original_pose_index, pose in enumerate(pose_data):
            if pose["x_position"] == original_pose_location["x_position"] and pose["y_position"] == original_pose_location["y_position"]:
                break

        # Throw an error if it tries to find a pose that doesn't exist
        if original_pose_index == None:
            print(json.dumps({"type":"error","value":0,"info_text":"image_prep_data searched for a pose that is not part of pose_data"}))
            raise Exception
        
        image_data.append({
            "path": f"{str(i).rjust(number_of_characters, '0')}.png",
            "original_pose_index": original_pose_index,
            "original_layer_index": image_prep["original_layer_index"]
        })

        # For updating progress bar. To prevent being called constantly, does a little math
        new_percent = math.floor((len(images) / len(image_prep_data)) * 100)
        if new_percent > curr_percent:
            curr_percent = new_percent
            update_progress("update", new_percent, "Generating images..." + f"({len(images)})")

    return image_data, images

# Input a layer image to get the position from, and a layer image to draw with
def generate_image_from_layers(original_layer_image, source_layer_image, pose_box, padding):
    # Get image position
    original_image = original_layer_image.crop(pose_box)
    original_bbox = original_image.getbbox()
    bound_original_image = original_image.crop(original_bbox)
    offset = (padding[0] - original_bbox[0], padding[1] - original_bbox[1])
    size = ((bound_original_image.width + padding[0] + padding[2]), (bound_original_image.height + padding[1] + padding[3]))

    # Make image
    return generate_image_from_source_layer(source_layer_image, pose_box, size, offset)

# Input a source image and a position, get an image
def generate_image_from_source_layer(source_layer_image, pose_box, size, offset):
    return generate_image(source_layer_image.crop(pose_box), size, offset)

# Generate a new image with the given input image, size, and offset
def generate_image(input_image, size, offset):
    image = Image.new("RGBA", size, (0,0,0,0)) # Create new image
    image.paste(input_image, offset) # Paste input image at position
    return image

# Generate data about the layers used, and return layer images as well
# TODO rework a little at some point. It works, though
def generate_layer_data(input_layer_data):
    output_layer_data = []
    search_images = []
    source_images = []
    
    number_of_characters = len(str(len(input_layer_data)))

    # Check every single layer for search and source image paths, and format them according to the layer's settings
    for i, layer in enumerate(input_layer_data): # Could probably do most of this better
        search_image_path = None
        source_image_path = None

        if layer["export_layer_images"]: # Now TECHNICALLY redundant, since this check is done when the images are saved in generate_sheet_data(), but idk I like it in both places. (IT MIGHT NOT BE THERE ANY MORE???)

            if layer["search_image_path"]:
                search_image_path = (
                    f"""layer{str(i + 1).rjust(number_of_characters, '0')}_{(f'''{(
                        'border' if layer.get('is_border') else (
                        f"{layer['name']}_original{(
                            '_cosmetic_layer' if layer.get('is_cosmetic_only') else ('_search' if layer.get('source_image_path') else '')
                        )}")
                    )}''')}_image_copy.png"""
                )

                with Image.open(layer["search_image_path"]) as search_image:
                    search_images.append(search_image.copy())

            else:
                search_images.append(None)
            if layer["source_image_path"]:
                source_image_path = f"layer{str(i + 1).rjust(number_of_characters, '0')}_{layer['name']}_original_source_image_copy.png"

                with Image.open(layer["source_image_path"]) as source_image:
                    source_images.append(source_image.copy())

            else:
                source_images.append(None)
        else:
            search_images.append(None)
            source_images.append(None) 

        output_layer_data.append({
            "name": layer["name"],
            "search_image_path": (os.path.basename(search_image_path) if search_image_path else None),
            "source_image_path": (os.path.basename(source_image_path) if source_image_path else None),
            "is_border": layer.get("is_border") == True, "is_cosmetic_only": layer.get("is_cosmetic_only") == True,
            "export_layer_images": layer.get("export_layer_images") == True
        })

    return output_layer_data, search_images, source_images

# Compare images. Return whether the two images are identical; if they are, also return image's flip and rotation relative to compare_to
# Return vals: is_unique, is_flipped, rotation_amount
def compare_images(curr_image_bytes_set : list[bytes], curr_image_sizes_set : list[tuple[int, int]],
                   compare_image_bytes : bytes, compare_image_size : tuple[int, int]):
    for i in range(len(curr_image_sizes_set)):
        # Stored byte/size are None at a given index if the relevant detect type for that index is not selected in menu_layerselect
        if curr_image_sizes_set[i]:
            # The bytes of the image are compared, to make sure all contained pixels are identical
            # The sizes are also compared, as bytes do not account for that, and theoretically differently-sized images could have identical pixel info
            if curr_image_bytes_set[i] == compare_image_bytes and curr_image_sizes_set[i] == compare_image_size:
                is_flipped = False
                rotation_amount = 0 # Rotation: 0 = 0 degreees, 1 = 90 degrees, 2 = 180 degrees, 3 = 270 degrees

                match i: # Indexes are organized as so because I THINK this is in order of how likely they are
                    # case 0: # Unmodified img; Doesn't need to exist as these are the default vals
                    case 1: # flip h
                        is_flipped = True
                    case 2: # rotate 90
                        rotation_amount = 1
                    case 3: # rotate 180
                        rotation_amount = 2
                    case 4: # rotate 270
                        rotation_amount = 3
                    case 5: # flip h, rotate 90
                        is_flipped = True
                        rotation_amount = 1
                    case 6: # flip h, rotate 180
                        is_flipped = True
                        rotation_amount = 2
                    case 7: # flip h, rotate 270
                        is_flipped = True
                        rotation_amount = 3
                    case 8: # flip v (the same as flip h + rotate 180)
                        is_flipped = True
                        rotation_amount = 2

                return False, is_flipped, rotation_amount # Return appropriate info
    
    # Getting here doesn't mean the image IS unique OVERALL - it still likely has to check against many more images
    return True, False, 0

# Generate one image that contains all selected layers merged together
def export_sheet_image(selected_layers, data, input_folder_path, output_folder_path, file_type):
    size = (data["header"]["width"], data["header"]["height"])
    layer_images = place_pose_images(
        data["image_data"],
        generate_image_placement_data(selected_layers, False, data["pose_data"], data["layer_data"], data["image_data"]), data["layer_data"],
        size,
        input_folder_path
    )

    sheet_image = Image.new("RGBA", size, (0,0,0,0))

    for i, layer_image in enumerate(layer_images): # probably a better way to do this
        if not i in selected_layers: layer_images.pop(i)

    for layer_image in reversed(layer_images):
        sheet_image.alpha_composite(layer_image)

    sheet_image.save(os.path.join(output_folder_path, f"{data["header"]["name"]}_sheet_export{file_type}")) # TODO ALWAYS make sure that supported filetypes work naturally with PIL. particularly worried about .bmp

# Generate an image for each selected layer
def export_layer_images(selected_layers, pose_type, data, input_folder_path, output_folder_path, file_type):
    unique_only = pose_type > 0

    size = (data["header"]["width"], data["header"]["height"])
    layer_images = place_pose_images(
        data["image_data"],
        generate_image_placement_data(selected_layers, unique_only, data["pose_data"], data["layer_data"], data["image_data"]),
        data["layer_data"],
        size,
        input_folder_path
    )

    number_of_characters = len(str(len(layer_images)))

    for i, layer_image in enumerate(layer_images):
        if i in selected_layers:
            path = (f"{data["header"]["name"]}_layer{str(i + 1).rjust(number_of_characters, '0')}_{data["layer_data"][i]["name"]}_export{file_type}") # TODO once filetype is selectable, add it here. do the same for the single merged image, too
            layer_image.save(os.path.join(output_folder_path, path))

# Export to a multilayer file. (At the moment, the only supported filetype is .aseprite, but this SHOULD change really soon! TODO UPDATE DESC)
def export_multilayer_file(selected_layers, pose_type, data, input_folder_path, output_folder_path, file_type):
    match file_type:
        case ".aseprite":
            export_aseprite(selected_layers, pose_type, data, input_folder_path, output_folder_path)
        case ".psd":
            export_psd(selected_layers, pose_type, data, input_folder_path, output_folder_path)

# Export an .aseprite file with the given info.
def export_aseprite(selected_layers, pose_type, data, input_folder_path, output_folder_path):
    update_progress("update", 0, "Exporting...", "Preparing to export to .aseprite...")
    
    # In theory, could move these to export_multilayer_file, but I like 'em standalone and also what if the weird handling of layer groups is drasically different between filetypes
    all_layer_images = []
    unique_layer_images = []
    size = (data["header"]["width"], data["header"]["height"])

    if pose_type != 1: # Layer images that contain all pose images
        all_layer_images = list(reversed(place_pose_images( # Lists are reversed consistently, because Aseprite handles layer order from bottom to top
            data["image_data"],
            generate_image_placement_data(selected_layers, False, data["pose_data"], data["layer_data"], data["image_data"]),
            data["layer_data"],
            size,
            input_folder_path
        )))

    if pose_type != 0: # Layer images that contain only unique pose images
        unique_layer_images = list(reversed(place_pose_images(
            data["image_data"],
            generate_image_placement_data(selected_layers, True, data["pose_data"], data["layer_data"], data["image_data"]),
            data["layer_data"],
            size,
            input_folder_path
        )))

    layer_images = []
    layer_names = []
    if pose_type == 2:
        # If pose_type "both" was selected, add layer images together, plus gaps for layer groups.
        # Speaking of layer groups: for some reason, they need to be placed BEFORE the layers in that group, which DOES make sense from
        # a top-to-bottom order, but not a bottom-to-top order? So, basically, the position of the group in the VISIBLE layer hierarcy
        # inside the Aseprite editor itself is misleading - the groups need to be "below" the layers they hold.
        layer_images = [None] + all_layer_images + [None] + unique_layer_images

        layer_names.append("all")
        layer_names += list(reversed([(layer.get("name") + "_all") for layer in data["layer_data"]]))
        layer_names.append("unique")
        layer_names += list(reversed([layer.get("name") for layer in data["layer_data"]]))
    else:
        layer_images = all_layer_images + unique_layer_images

        layer_names = list(reversed([layer.get("name") for layer in data["layer_data"]]))

    num_of_layers = len(data["layer_data"])
    cels = []

    layers = []
    for i, layer_name in enumerate(layer_names):
        layers.append({
            "name": layer_name,
            "layer_type": 0 if (i % (num_of_layers + 1)) or pose_type != 2 else 1, # 0 == normal image layer, 1 == group
            "child_level": 1 if (i % (num_of_layers + 1)) and pose_type == 2 else 0 # 1 == inside group, 0 == outside group OR is itself a group
        })

    for i, layer_image in enumerate(layer_images):
        if layers[i].get("layer_type") == 0: # If this is a normal image layer:
            cels.append({
                "image": layer_image, # Shouldn't be None, because the indexes of the groups should match the Nones inserted above
                "layer_index": i,
                "z_index": num_of_layers if (i < num_of_layers) and pose_type == 2 else 0
            })
    
    update_progress("update", 50, "Exporting...", "Saving to .aseprite...")
    formatted = aseprite_file.format_simple_dicts(size, layers, cels) # The layers and cels are inputted in a format that can be cleaned up and saved below
    aseprite_file.save(formatted, os.path.join(output_folder_path, f"{data["header"]["name"]}_sheet_export.aseprite"))

# Export a .psd file with the given info.
def export_psd(selected_layers, pose_type, data, input_folder_path, output_folder_path):
    update_progress("update", 0, "Exporting...", "Preparing to export to .psd...")

    all_layer_images = []
    unique_layer_images = []
    size = (data["header"]["width"], data["header"]["height"])
    width = size[0]
    height = size[1]
    offset_x = math.ceil(width/2)
    offset_y = math.ceil(height/2)

    if pose_type != 1: # Layer images that contain all pose images
        all_layer_images = list(place_pose_images(
            data["image_data"],
            generate_image_placement_data(selected_layers, False, data["pose_data"], data["layer_data"], data["image_data"]),
            data["layer_data"],
            size,
            input_folder_path
        ))

    if pose_type != 0: # Layer images that contain only unique pose images
        unique_layer_images = list(place_pose_images(
            data["image_data"],
            generate_image_placement_data(selected_layers, True, data["pose_data"], data["layer_data"], data["image_data"]),
            data["layer_data"],
            size,
            input_folder_path
        ))
    
    layer_images : list[Image.Image] = []
    layer_names : list[str] = []
    if pose_type == 2:
        # If pose_type "both" was selected, add layer images together, plus gaps for layer groups.
        # Speaking of layer groups: for some reason, they need to be placed BEFORE the layers in that group, which DOES make sense from
        # a top-to-bottom order, but not a bottom-to-top order? So, basically, the position of the group in the VISIBLE layer hierarcy
        # inside the Aseprite editor itself is misleading - the groups need to be "below" the layers they hold.
        layer_images = [None] + unique_layer_images + [None] + all_layer_images

        layer_names.append("unique")
        layer_names += [layer.get("name") for layer in data["layer_data"]]
        layer_names.append("all")
        layer_names += [(layer.get("name") + "_all") for layer in data["layer_data"]]
    else:
        layer_images = unique_layer_images + all_layer_images

        layer_names = [layer.get("name") for layer in data["layer_data"]]

    color_mode = psapi.enum.ColorMode.rgb
    document = psapi.LayeredFile_8bit(color_mode, width, height)
    last_group = None

    for i, layer_image in enumerate(layer_images):
        if layer_image != None: # If layer_image == None, it's a layer group. TODO this is unsafe, as unchecking Export for a layer may make that qualify as a layer group!
            img_data = numpy.zeros((4, height, width), numpy.uint8)
            
            # PhotoshopAPI library requires the images to be separated into channels
            r = layer_image.getchannel("R")
            g = layer_image.getchannel("G")
            b = layer_image.getchannel("B")
            a = layer_image.getchannel("A")
            img_data[0] = numpy.asarray(r)
            img_data[1] = numpy.asarray(g)
            img_data[2] = numpy.asarray(b)
            img_data[3] = numpy.asarray(a)

            # Create image layer
            img_layer = psapi.ImageLayer_8bit(img_data, layer_names[i], width=width, height=height, pos_x=offset_x, pos_y=offset_y)

            if last_group != None:
                last_group.add_layer(document, img_layer)
            else:
                document.add_layer(img_layer)
        else:
            group_layer = psapi.GroupLayer_8bit(layer_names[i])
            document.add_layer(group_layer)
            last_group = group_layer

    document.write(os.path.join(output_folder_path, f"{data["header"]["name"]}_sheet_export.psd"))

# Re-format pose, layer, and image data so that limb data is per-image, not per-pose.
def generate_image_placement_data(selected_layers, pose_type, pose_data, layer_data, image_data):
    layer_names = [layer.get("name") for layer in layer_data]

    unique_only = pose_type > 0 # pose_type: 0 == all, 1 == unique only. 2 is only for multilayer, and should be disabled here, since it's not multilayer.

    image_placement_data = []
    for _ in range(len(image_data)):
        image_placement_data.append([])
    
    curr_percent = 0 # Exists to prevent near-constant calls to update_progress later on

    # Look through all poses for limbs; add the pose's position/size to each limb's referenced image index
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
                    image_placement_data[image_index].append({
                        "x_position": x_position + x_offset,
                        "y_position": y_position + y_offset,
                        "layer_index": layer_index,
                        "flip_h": limb["flip_h"],
                        "rotation_amount": limb["rotation_amount"]
                    })
        
        # For updating progress bar. To prevent being called constantly, does a little math
        new_percent = math.floor((pose_index / len(pose_data)) * 100)
        if new_percent > curr_percent:
            curr_percent = new_percent
            update_progress("update", new_percent, "Exporting...", f"Formatting poses: ({pose_index + 1}/{len(pose_data)})")

    # dawning on me that we can check for original pose index if we simply look through pose data for the first instance. we're kinda doing that anyway. think abt this
    return image_placement_data

# Place pose images according to image_placement_data
def place_pose_images(image_data, image_placement_data, layer_data, size, input_folder_path):
    # Pose images will be placed onto layer images, which will all be returned at the end
    layer_images = [None] * len(layer_data)
    img_base = Image.new("RGBA", size, (0,0,0,0))

    for i, layer in enumerate(layer_data):
        if layer["is_border"] or layer["is_cosmetic_only"]:
            path = os.path.join(input_folder_path, layer["search_image_path"])
            with Image.open(path) as image:
                layer_images[i] = image.copy()
        else:
            layer_images[i] = img_base.copy()
    
    # Iterate through each image
    for i, image_placement in enumerate(image_placement_data):
        with Image.open(os.path.join(input_folder_path, image_data[i]["path"])) as image:
            
            # Iterate through each instance of each image
            for limb_placement in image_placement:
                if limb_placement != None and layer_images[limb_placement["layer_index"]] != None:
                    adjusted_image = image.copy()

                    # I've never been sure why, but I've had to rotate backwards pretty consistently. Am I storing the info wrong or something? I don't THINK so, right???
                    match limb_placement["rotation_amount"]:
                        case 1:
                            adjusted_image = adjusted_image.transpose(Image.Transpose.ROTATE_270)
                        case 2:
                            adjusted_image = adjusted_image.transpose(Image.Transpose.ROTATE_180)
                        case 3:
                            adjusted_image = adjusted_image.transpose(Image.Transpose.ROTATE_90)
                    
                    if limb_placement["flip_h"]: adjusted_image = adjusted_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

                    layer_images[limb_placement["layer_index"]].alpha_composite(adjusted_image, (limb_placement["x_position"], limb_placement["y_position"]))

    return layer_images
    
# Opens the new layer images that will be used to update the pose images, and then passes them along to update_pose_images()
def update_pose_images_with_images(update_image_paths, data, input_folder_path):
    update_layer_images = [None] * len(update_image_paths) # Pre-format the list for simplicity
    for i, new_image_path in enumerate(update_image_paths):
        if new_image_path:
            with Image.open(new_image_path) as new_layer_image:
                update_layer_images[i] = new_layer_image.copy() # Make copies of the images, so that we don't have to keep the files open

    # Update the pose images
    update_pose_images(update_layer_images, data, input_folder_path)

# Gets the new layer images from the multilayer file using the respective function, then passes them along to update_pose_images()
def update_pose_images_with_multilayer_file(multilayer_file_path, selected_layers, data, input_folder_path):
    extension = os.path.splitext(multilayer_file_path)[1] # Get the extension
    images : list[Image.Image] = []

    if extension == ".ase" or extension == ".aseprite":
        update_progress("update", 0, "Updating pose images...", "Reading .aseprite file...")
        images = get_layer_images_from_aseprite(multilayer_file_path, selected_layers, data) # Get .aseprite cels as PIL images
    elif extension == ".psd": # May add other filetypes to this if they're identical
        update_progress("update", 0, "Updating pose images...", "Reading .psd file...")
        images = get_layer_images_from_psd(multilayer_file_path, selected_layers, data) # Get .psd ImageLayer image_data as PIL images

    # Update the pose images
    update_pose_images(images, data, input_folder_path)

# If the selected layers exist, get and return them from the .aseprite file
def get_layer_images_from_aseprite(aseprite_file_path, selected_layers, data) -> list[Image.Image]:
    # Get dict that holds .aseprite's data
    sprite_dict = aseprite_file.load(aseprite_file_path)

    cels = aseprite_file.get_all_chunks_of_type(sprite_dict, aseprite_file.CEL_CHUNK) # Cels contain the images, and an index for the layer they're part of
    layers = aseprite_file.get_all_chunks_of_type(sprite_dict, aseprite_file.LAYER_CHUNK) # Layers contain the names, which are matched against json's layer_data

    layer_names_from_json_data = [layer.get("name") for layer in data.get("layer_data")] # Layer names. I gave this a long name because the "layers" variable above would've confused me otherwise

    size = (data["header"]["width"], data["header"]["height"]) # Image size
    img_base = Image.new("RGBA", size, (0,0,0,0)) # A basic transparent image that the cels are pasted onto
    images : list[Image.Image] = [None] * len(layer_names_from_json_data) # Pre-format list for simplicity

    for i, name in enumerate(layer_names_from_json_data): # Go off of layer names, as those will match the actual json's layer_data much better than the .aseprite
        if i in selected_layers:
            for j, layer in enumerate(layers): # There's a VERY good chance that the num of layers and their indexes won't match between input .aseprite and json's layer_data...
                if layer.get("name") == name: # ...so instead we match by name. Not a perfect system, could allow for manual selection later. This works for now.
                    cel = next(cel for cel in cels if cel.get("layer_index") == j) # Get the cel that matches this layer's index
                    image = img_base.copy() # Copy base image
                    image.paste(cel.get("image"), (cel.get("x_pos"), cel.get("y_pos"))) # Paste cel image, which is likely smaller than needed & has a stored offset
                    images[i] = image # Set the image at the index
    
    # TODO print something if a selected layer was not found in the .aseprite?

    return images

# If the selected layers exist, get and return them from the .psd file
def get_layer_images_from_psd(psd_file_path, selected_layers, data):
    psd_file = psapi.LayeredFile.read(psd_file_path)
    layer_names_from_json_data = [layer.get("name") for layer in data.get("layer_data")]
    images : list[Image.Image] = [None] * len(layer_names_from_json_data)

    for layer in psd_file.flat_layers: # TODO check this! the library's pretty inconsistent, so this name might change
        try:
            # This returns an error if the name's not found, so it's wrapped in a try/except that does nothing
            curr_layer_index = layer_names_from_json_data.index(layer.name) # Layer name indexes are always consistent with json's layer_data, and that's not a guarantee with the .psd's layers
        except ValueError:
            continue

        if curr_layer_index in selected_layers:
            # Get each channel, because this library is freakin' weird and if I used get_image_data I'd get a DICT that contains everything organized by channel anyway!
            r = layer.get_channel_by_id(psapi.enum.ChannelID.red)
            g = layer.get_channel_by_id(psapi.enum.ChannelID.green)
            b = layer.get_channel_by_id(psapi.enum.ChannelID.blue)
            a = layer.get_channel_by_id(psapi.enum.ChannelID.alpha)

            img_data = numpy.stack((r, g, b, a), axis=-1) # Use numpy to reformat the individual channels into a single list, with each pixel now represented by a list: [r, g, b, a]
            image : Image.Image = Image.fromarray(img_data) # Get PIL image
            images[curr_layer_index] = image
    
    # TODO print something if a selected layer was not found in the .psd?

    return images

# Use several layer images to update the pose images
def update_pose_images(images, data, input_folder_path):
    curr_percent = 0 # Exists to prevent near-constant calls to update_progress later on

    for i, image_datum in enumerate(data["image_data"]):

        layer_index = image_datum["original_layer_index"]
        if images[layer_index] != None:

            pose = data["pose_data"][image_datum["original_pose_index"]]
            pose_box = (pose["x_position"], pose["y_position"], pose["x_position"] + pose["width"], pose["y_position"] + pose["height"])

            # Get a limb from this pose that's part of the correct layer. It would be fairly trivial to prevent an error from happening if no limb
            # is found, but on the other hand, maybe it SHOULD raise an error if limbs are not found where they're expected. After all, this is
            # searching for the ORIGINAL limb locations, so there can only NOT be something there if the data was modified in some way.
            limb = next(l for l in pose["limb_data"] if l["layer_index"] == layer_index)

            with Image.open(os.path.join(input_folder_path, image_datum["path"])) as image:
                size = image.size
                
            # Admittedly not sure why we're using the negative offsets, but this is the only way this works. I am not good at math
            offset = (-limb["x_offset"], -limb["y_offset"])

            # Generate image
            generate_image_from_source_layer(
                images[image_datum["original_layer_index"]], pose_box, size, offset
            ).save(os.path.join(input_folder_path, image_datum["path"]))

        # For updating progress bar. To prevent being called constantly, does a little math
        new_percent = math.floor((i / len(data["image_data"])) * 100)
        if new_percent > curr_percent:
            curr_percent = new_percent
            update_progress("update", new_percent, "Updating pose images...", f"Updated: ({i + 1}/{len(data['image_data'])})")

# Given the search settings, calculate the range or ranges to search.
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