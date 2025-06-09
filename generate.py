from PIL import Image, ImageColor
# from tkinter import messagebox
from itertools import chain
from datetime import datetime
import json
import math

import os
# import time
import psutil

# from shared import consistxels_version

consistxels_version = "0.1"

# import time

# def generate(pipe_conn):
#     for i in range(5):
#         msg = {"progress": i + 1}
#         pipe_conn.send(msg)
#         time.sleep(0.5)  # Simulate work

#     pipe_conn.send({"status": "done"})
#     ack = pipe_conn.recv()  # Wait for ack before exiting
#     if ack == "ack":
#         pipe_conn.close()

# Made so that all functions here CAN be used with a progress bar, but don't NEED one to work
# def update_progress(progress_callback = None, new_value = None, progress_text = None):
# def update_progress(progress_callback = None, value = None, header_text = None, info_text = None):
# def update_progress(conn = None, new_value = None, section_text = None, progress_text = None):
def update_progress(type="update", value = None, header_text = None, info_text = None):
    # update = {"value": value, "header_text": header_text, "info_text": info_text}
    # print(json.dumps(update), flush=True)


    # if progress_callback != None:
    #     progress_callback(value, header_text, info_text)

    # might want to do some exception stuff!
    # if conn != None:
    #     conn.send(("update", new_value, section_text, progress_text))

    # p = psutil.Process(os.getpid())
    # update = {"status": status, "value": value, "header_text": header_text, "info_text": info_text, "priority": p.nice()}
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
        input_header = input_data["header"]
        input_layer_data = input_data["layer_data"]
        input_pose_data = input_data["pose_data"]

        # Also taken from input, but simply used in output as they are, with no modification
        search_data = input_data["search_data"]
        search_type_data = input_data["search_type_data"]
        generation_data = input_data["generation_data"]

        # Size is used in a few places, especially when generating full output in menu_loadjson, so it's calculated and stored in the header.
        # TODO: Throw exception if size is still (0,0) after that. Or I guess if either height or width is still 0, neither should be after all
        size = (0,0)
        layer = next(layer for layer in input_layer_data if (layer.get("search_image_path") or layer.get("source_image_path")))
        with Image.open(layer["search_image_path"] if layer.get("search_image_path") else layer["source_image_path"]) as img:
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
        output_layer_data, search_images, source_images = generate_layer_data(input_layer_data, output_dir, input_header["paths_are_local"])

        for i in range(len(search_images)):
            # print("saving image", i)
            # images[i].save(output_folder_path + image_data[i]["path"])
            if search_images[i]:
                
                image_path = output_layer_data[i]["search_image_path"]
                if input_header["paths_are_local"]: image_path = os.path.join(output_dir, output_layer_data[i]["search_image_path"])
                
                search_images[i].save(image_path)

        for i in range(len(source_images)):
            # print("saving image", i)
            # images[i].save(output_folder_path + image_data[i]["path"])
            if source_images[i]:
                
                image_path = output_layer_data[i]["source_image_path"]
                if input_header["paths_are_local"]: image_path = os.path.join(output_dir, output_layer_data[i]["source_image_path"])
                
                source_images[i].save(image_path)

        # update_progress(progress_callback, 75, "Wrapping up; saving output to .json...")
        # update_progress(conn, 75, "Wrapping up; saving output to .json...")

        # Structure output
        output_header = {
            "name": input_header["name"],
            "consistxels_version": consistxels_version,
            "paths_are_local": input_header["paths_are_local"],
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
        update_progress("error", 0, "An error occured", e)
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

def generate_layer_data(input_layer_data, output_folder_path, paths_are_local):
    output_layer_data = []
    search_images = []
    source_images = []
    
    for layer in input_layer_data:
        search_image_path = None
        source_image_path = None

        if layer["export_original_images"]:

            if layer["search_image_path"]:
                search_image_path = (
                    (f"{layer['name']}_" + ("search" if layer["source_image_path"] else "layer") + "_image.png")
                    if not layer["is_border"] else
                    "border.png"
                )

                with Image.open(layer["search_image_path"]) as search_image:
                    # search_image.save(output_folder_path + search_image_path)
                    search_images.append(search_image.copy())

                # if not paths_are_local: search_image_path = output_folder_path + search_image_path
                # if not paths_are_local: search_image_path = output_folder_path + "/" + search_image_path
                if not paths_are_local: search_image_path = os.path.join(output_folder_path, search_image_path)
            else:
                search_images.append(None)
            if layer["source_image_path"]:
                source_image_path = f"{layer['name']}_source_image.png"

                with Image.open(layer["source_image_path"]) as source_image:
                    # source_image.save(output_folder_path + source_image_path)
                    source_images.append(source_image.copy())

                # if not paths_are_local: source_image_path = output_folder_path + source_image_path
                # if not paths_are_local: source_image_path = output_folder_path + "/" + source_image_path
                if not paths_are_local: source_image_path = os.path.join(output_folder_path, source_image_path)
            else:
                source_images.append(None)

        output_layer_data.append({
            "name": layer["name"], "is_border": layer["is_border"], "is_cosmetic_only": layer["is_cosmetic_only"],
            "search_image_path": search_image_path, "source_image_path": source_image_path
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

# # import time
# # import sys

# # def heavy_task():
# #     total_steps = 20
# #     for i in range(total_steps):
# #         # Simulate CPU-heavy work (replace with your Pillow code)
# #         time.sleep(0.5)
# #         progress = int((i + 1) / total_steps * 100)
# #         print(progress)
# #         sys.stdout.flush()  # Important: flush so parent can read immediately

# # if __name__ == "__main__":
# #     heavy_task()

# # generate.py
# import math
# import sys
# import time

# def is_prime(n):
#     if n < 2:
#         return False
#     for i in range(2, int(math.sqrt(n)) + 1):
#         if n % i == 0:
#             return False
#     return True

# def heavy_cpu_task():
#     max_number = 4000000  # Adjust this to make it more/less intense
#     found = 0
#     last_report = 0

#     for i in range(2, max_number):
#         if is_prime(i):
#             found += 1
#         # Print progress every 5%
#         progress = int(i / max_number * 100)
#         if progress != last_report and progress % 5 == 0:
#             print(progress)
#             sys.stdout.flush()
#             last_report = progress

#     print("100")  # Ensure it ends at 100%
#     sys.stdout.flush()

# if __name__ == "__main__":
#     # start = time.time()
#     heavy_cpu_task()
#     # end = time.time()
#     # print(f"Elapsed: {end - start:.2f}s", file=sys.stderr)
