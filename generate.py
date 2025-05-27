from PIL import Image, ImageColor
# import numpy as np
from numpy import asarray
from tkinter import filedialog
import json
import math
from itertools import chain
# from datetime import date

# I probably should've split this into a few smaller functions. Oh well *shrug*
# padding_type: 0 = minimize (show only pixels that WILL show up on final sheet), 1 = maximize (show ALL pixels that COULD THEORETICALLY end up on sheet), 2 = custom amount
def GenerateJSON(output_name, border_image_path, border_color, image_info, start_search_in_center = True, search_right_to_left = False, padding_type = 0, custom_padding = 0):

    border_image = Image.open(border_image_path) # get image

    border_image_array = asarray(border_image) # get image as array

    height, width = border_image_array.shape[:2] # get height and width of image

    # get border_color (needs to have an alpha channel)
    # border_color_rgb = ImageColor.getrgb("#00007fff")
    border_color_rgb = ImageColor.getrgb(border_color + "ff")

    # for storing unique images!
    # specifically, will store the image, and its minimum padding (make min or max padding a setting? just min for now i guess)
    # format: [{"img", "left_padding", "top_padding", "right_padding", "bottom_padding"}]
    image_object_array = []

    # for storing pose information, which will be output in .json format
    # format:
    # [{
    #   "name",
    #   "x_position",
    #   "y_position",
    #   "width",
    #   "height",
    #   "limb_objects" = [{}]
    # }]
    pose_objects = []

    # opening layer images here so that we don't have to re-open and -close them over and over while searching for poses 
    layer_images = []
    for layer_data in image_info:
        layer_images.append(Image.open(layer_data["path"]))

    # and for good measure, limb_objects format:
    # [{"x_offset", "y_offset", "image_index", "flip_h", "rotation"}]
    # this is specifically limbs that are PART OF a pose, not just saved limb images. so these contain pose-specific data, and are not interchangeable,
    # even if they reference the same limb image.
    # also, the image they reference is gonna be a number - and that'll reference the number of images, i think??? like, there are 99 images in
    # a given images folder, and the number can just double as the filename
    # also also, "offset" is referring to how far off the top-left corner of the sprite is from the top-left corner of the pose box.
    # also also also, "flip_h" does what it says on the tin (it's a bool), and "rotation" stores an int, and increments rotation by 90 degrees

    

    # always subtracting 2 from the ranges, because there is no pose that can fit in a 2-wide or 2-high box, inclusive of border - there's no space
    for y in range(height - 2): # rows
        # This is where the right-to-left searching or left-to-right searching is decided
        # for x in (range(width - 2, -1, -1) if search_right_to_left else range(width - 2)): # columns
        for x in (get_x_range(0, width, start_search_in_center, search_right_to_left)): # columns

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
                    
                    # iterate all the way to the right. if no border is found, it's not a pose box after all.
                    for x2 in range(x + 1, width):
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

                # We COULD not save completely-empty poses. TODO: think about this more. Would need to go much later - i.e. where they're actually saved
                # But there IS value in making pose box json even if there's no sprite there. After all, the box is still there in the provided
                # border, at least.

                # x and y coordinate are moved right and down 1, so that they're INSIDE the pose box, rather than on its border
                found_pose_x = x + 1
                found_pose_y = y + 1
                found_pose_width = endborder_x - x - 1
                found_pose_height = endborder_y - y - 1

                # creation of pose object
                pose_object = {
                    "name": "pose_" + str(found_pose_x) + "_" + str(found_pose_y), # maybe think of better name?
                    "x_position": found_pose_x,
                    "y_position": found_pose_y,
                    "width": found_pose_width,
                    "height": found_pose_height,
                    "limb_objects": []
                }
                
                layer_index = 0 # i hate this so much i gotta go eat dinner

                # now, search through every layer for sprites
                for layer_data in image_info:

                    # we already opened the layer images provided, so that we don't have to open and close them every time we find a pose box
                    curr_layer_image = layer_images[layer_index]
                    layer_index += 1
                    
                    curr_layer_name = layer_data["name"]

                    # crop parameter tuple: (left, top, right, bottom)
                    test_val_tuple = (found_pose_x, found_pose_y, endborder_x, endborder_y) # not endborder_x - 1, for some reason. cut off a pixel that way

                    unbound_image = curr_layer_image.crop(test_val_tuple) # the full image inside the pose box

                    # testimg = Image.new("RGBA", (2,2))
                    # testimg.transpose()

                    # the rectangle inside the image that actually contains a sprite - everything else is just transparent pixels
                    bbox = unbound_image.getbbox()
                    # print(bbox)
                    
                    # getbbox() returns None if there's no sprite, so this is verifying that there's even a sprite in the first place
                    if bbox:
                        # store info implied by bounding box - i.e. offset. this is for formatting purposes in export, BUT ALSO for deciding maximum bounds for each limb

                        # crop image down to bounding box, so that it can be compared to other stored images
                        bound_image = unbound_image.crop(bbox)
                        
                        # loop control
                        image_is_unique = True
                        image_index = 0

                        # info for posed limbs, declared outside the loop so that they persist, but i dunno if python works like that
                        is_flipped = False # whether the image is flipped horizontally
                        rotation_amount = 0 # increment by 1, each represents 90 degrees

                        # check against stored images - check w/ flip_h, flip_y, & rotate. so like 12 checks per limb :(
                        for data in image_object_array:

                            img = data["img"] # get img from 

                            if bound_image.tobytes() == img.tobytes(): # the bound image is already stored; move on
                                image_is_unique = False
                                break
                            
                            # prepare a flipped version of the img, since it'll commonly be an already-stored img, and it's in a lotta checks
                            flip_h = bound_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                            
                            if flip_h.tobytes() == img.tobytes(): # the flipped image is already stored; move on
                                image_is_unique = False
                                is_flipped = True
                                break
                            
                            # rotate normal image 90 degrees
                            if bound_image.transpose(Image.Transpose.ROTATE_90).tobytes() == img.tobytes():
                                image_is_unique = False
                                rotation_amount = 1
                                break

                            # rotate normal image 180 degrees
                            if bound_image.transpose(Image.Transpose.ROTATE_180).tobytes() == img.tobytes():
                                image_is_unique = False
                                rotation_amount = 2
                                # print(curr_layer_name, bbox)
                                break

                            # rotate normal image 270 degrees
                            if bound_image.transpose(Image.Transpose.ROTATE_270).tobytes() == img.tobytes():
                                image_is_unique = False
                                rotation_amount = 3
                                break
                            
                            # rotate flipped image 270 degrees (i.e. -90 degrees, 'cause it's flipped)
                            if flip_h.transpose(Image.Transpose.ROTATE_270).tobytes() == img.tobytes():
                                image_is_unique = False
                                is_flipped = True
                                rotation_amount = 3
                                break

                            # rotate flipped image 180 degrees
                            if flip_h.transpose(Image.Transpose.ROTATE_180).tobytes() == img.tobytes():
                                image_is_unique = False
                                is_flipped = True
                                rotation_amount = 2
                                break

                            # rotate flipped image 90 degrees (i.e. -270 degrees, 'cause it's flipped)
                            if flip_h.transpose(Image.Transpose.ROTATE_90).tobytes() == img.tobytes():
                                image_is_unique = False
                                is_flipped = True
                                rotation_amount = 1
                                break
                            
                            # LUCKILY FOR ME, don't need to check flip_v at all. It's equivalent to flip_h rotate 180 degrees. All rotations for flip have
                            # been checked, so no need to check flip_v.

                            image_index += 1

                        # padding is saved for a few reasons. mostly, it's there to make the sprites easier to edit in a separate program once
                        # they've been output. without the padding, there'd be no room to work with, and you'd need to increase the size of the sprites,
                        # and then everything would get cut off, and it'd just be a whole mess. minimum padding was chosen because it shows exactly
                        # where the padding can be such that nothing gets cut off, in any of the poses where the identical image is used. however,
                        # maximum padding, wherein one can choose to see maximum space available for even a single pose, even if it gets cut off,
                        # will also be available. as will custom padding values!!! so that's fun. TODO: make comment better

                        # print("\n", bbox)

                        
                        # left_padding = bbox[0]
                        # top_padding = bbox[1]
                        # right_padding = unbound_image.width - (left_padding + bound_image.width)
                        # print(bbox[2], bound_image.width)
                        # bottom_padding = unbound_image.height - (top_padding + bound_image.height) # maybe issue is here????????????

                        # right_padding = unbound_image.width - bbox[2]
                        # bottom_padding = unbound_image.height - bbox[3]

                        # match padding_type:
                        #     case 2:
                        #         left_padding, top_padding, right_padding, bottom_padding = custom_padding
                        #     case _:
                        #         left_padding = bbox[0]
                        #         top_padding = bbox[1]
                        #         right_padding = unbound_image.width - bbox[2]
                        #         bottom_padding = unbound_image.height - bbox[3]
                        
                        # print(custom_padding, type(custom_padding))
                        left_padding = top_padding = right_padding = bottom_padding = custom_padding

                        if padding_type != 2:
                            left_padding += bbox[0]
                            top_padding += bbox[1]
                            right_padding += unbound_image.width - bbox[2]
                            bottom_padding += unbound_image.height - bbox[3]

                        left_padding = max(0, left_padding)
                        top_padding = max(0, top_padding)
                        right_padding = max(0, right_padding)
                        bottom_padding = max(0, bottom_padding)

                        # left_padding, top_padding, right_padding, bottom_padding = bbox

                        if image_is_unique:
                            image_object_array.append({
                                "img": bound_image,
                                "width": bound_image.width,
                                "height": bound_image.height,
                                "left_padding": left_padding,
                                "top_padding": top_padding,
                                "right_padding": right_padding,
                                "bottom_padding": bottom_padding
                            })
                        # if making automatic padding, either minimize or maximize. don't need to do this for custom padding, since it'll be equal;
                        # rotating and flipping would do nothing
                        elif padding_type != 2: 
                            
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

                            match padding_type: # probably an even more efficient way to do this
                                case 0:
                                    image_object_array[image_index]["left_padding"] = min(image_object_array[image_index]["left_padding"], left_padding)
                                    image_object_array[image_index]["top_padding"] = min(image_object_array[image_index]["top_padding"], top_padding)
                                    image_object_array[image_index]["right_padding"] = min(image_object_array[image_index]["right_padding"], right_padding)
                                    image_object_array[image_index]["bottom_padding"] = min(image_object_array[image_index]["bottom_padding"], bottom_padding)
                                case 1:
                                    image_object_array[image_index]["left_padding"] = max(image_object_array[image_index]["left_padding"], left_padding)
                                    image_object_array[image_index]["top_padding"] = max(image_object_array[image_index]["top_padding"], top_padding)
                                    image_object_array[image_index]["right_padding"] = max(image_object_array[image_index]["right_padding"], right_padding)
                                    image_object_array[image_index]["bottom_padding"] = max(image_object_array[image_index]["bottom_padding"], bottom_padding)

                            # if image_object_array[image_index]["left_padding"] > left_padding:
                            #     image_object_array[image_index]["left_padding"] = left_padding
                            # if image_object_array[image_index]["top_padding"] > top_padding:
                            #     image_object_array[image_index]["top_padding"] = top_padding
                            # if image_object_array[image_index]["right_padding"] > right_padding:
                            #     image_object_array[image_index]["right_padding"] = right_padding
                            # if image_object_array[image_index]["bottom_padding"] > bottom_padding:
                            #     image_object_array[image_index]["bottom_padding"] = bottom_padding

                        # limb_object = {
                        #     "name": curr_layer_name,
                        #     "x_offset": left_padding, # PRETTY SURE this is correct. these padding variables are unaltered, and have to do with the unbound image
                        #     "y_offset": top_padding,
                        #     "image_index": image_index,
                        #     "flip_h": is_flipped,
                        #     "rotation": rotation_amount
                        # }

                        limb_object = {
                            "name": curr_layer_name,
                            "x_offset": bbox[0], # guess what ISN'T fucking unaltered, dipshit (if i forget to delete this comment and someone sees it: this took me 12 hours to figure out)
                            "y_offset": bbox[1],
                            "image_index": image_index,
                            "flip_h": is_flipped,
                            "rotation": rotation_amount
                        }

                        pose_object["limb_objects"].append(limb_object)

                        # and HERE'S where layer stuff stops mattering

                # some sort of dialog box that updates with what's currently going on, maybe? like a "Poses: ###"

                pose_objects.append(pose_object)
                print("Poses found: " + str(len(pose_objects)))

        print("Search: " + str(math.floor((y / (height - 2)) * 100)) + "%")
    print("Search complete")

    # ask for output location
    output_folder_path = filedialog.askdirectory(title="Select an output folder")

    # output_folder_path = output_folder_path.rstrip("/consistxels_output_" + output_name)
    # output_folder_path += "/consistxels_output_" + output_name

    # and then, here, we go through all poses, and all limbs, to update their padding according to the image index listed in the limb_object

    # go through pose list
    # - go through limb list
    # - reference img index's padding
    # - subtract left padding from x-offset, and top padding from y-offset
    for pose in pose_objects:
        for limb in pose["limb_objects"]:
            image_object = image_object_array[limb["image_index"]]

            image_left_padding = image_object["left_padding"]
            image_top_padding = image_object["top_padding"]
            image_right_padding = image_object["right_padding"]
            image_bottom_padding = image_object["bottom_padding"]
            
            if limb["flip_h"]:
                temp = image_left_padding
                image_left_padding = image_right_padding
                image_right_padding = temp

                paddings = [image_left_padding, image_top_padding, image_right_padding, image_bottom_padding]
                
                # Rotate padding values counterclockwise by 90-degree steps
                for _ in range(limb["rotation"]):
                    paddings = [paddings[1], paddings[2], paddings[3], paddings[0]]
            
                image_left_padding, image_top_padding, image_right_padding, image_bottom_padding = paddings
            else: 
                paddings = [image_left_padding, image_top_padding, image_right_padding, image_bottom_padding]

                # Rotate padding values clockwise by 90-degree steps
                for _ in range(limb["rotation"]):
                    paddings = [paddings[3], paddings[0], paddings[1], paddings[2]]

                image_left_padding, image_top_padding, image_right_padding, image_bottom_padding = paddings

            limb["x_offset"] -= image_left_padding
            limb["y_offset"] -= image_top_padding

            # match rotation_amount:
            #     case 1:
            #         temp = image_left_padding
            #         image_left_padding = image_bottom_padding
            #         image_bottom_padding = image_right_padding
            #         image_right_padding = image_top_padding
            #         image_top_padding = temp
            #     case 2:
            #         temp = image_top_padding
            #         image_top_padding = image_bottom_padding
            #         image_bottom_padding = temp
            #         temp = image_left_padding
            #         image_left_padding = image_right_padding
            #         image_right_padding = temp
            #     case 3:
            #         temp = image_left_padding
            #         image_left_padding = image_top_padding
            #         image_top_padding = image_right_padding
            #         image_right_padding = image_bottom_padding
            #         image_bottom_padding = temp


            # x_offset_adjust = -image_left_padding
            # y_offset_adjust = -image_top_padding


            # if (image_object["width"] % 2 != 0 or image_object["height"] % 2 != 0) and (limb["rotation"] == 2):
                # y_offset_adjust -= 1

            # limb["x_offset"] += x_offset_adjust
            # limb["y_offset"] += y_offset_adjust





    print("Limb offsets adjusted for padding")

    # go through img list
    # - update img size using padding
    # - save imgs!!! we'll need an output folder location, etc.
    color_transparent = ImageColor.getrgb("#00000000")
    number_of_characters = len(str(len(image_object_array)))

    image_index = 0

    # format: [image_path]
    images = []

    for image_object in image_object_array:
        image = image_object["img"]
        image_left_padding = image_object["left_padding"]
        image_top_padding = image_object["top_padding"]
        image_right_padding = image_object["right_padding"]
        image_bottom_padding = image_object["bottom_padding"]

        # print(str(image_bottom_padding))
        # print(str(image_bottom_padding))
        # print(str(image_bottom_padding))
        # print(str(image_bottom_padding))

        padded_image = Image.new("RGBA", ((image.width + image_left_padding + image_right_padding), (image.height + image_top_padding + image_bottom_padding)), color_transparent)
        padded_image.paste(image, (image_left_padding, image_top_padding))

        # image_path = output_folder_path + "/" + str(image_index).rjust(number_of_characters, "0") + ".png" # TODO: rather than saving relative path, just save image name. we already have the output folder!
        image_path = str(image_index).rjust(number_of_characters, "0") + ".png"
        images.append(image_path)
        # TODO: in GENERAL, the path stuff is... not my favorite. it's really dependant on the user's individual machine, and is therefore unable to be shared around. i COULD separately share the images, pose_objects, etc., that would be fine. i dunno. header relies on absolute paths for the border image, too. maybe that should just be included with the output?
        # (similarly: don't even NEED the layer paths, if ya think about it, only the names!)

        padded_image.save(output_folder_path + "/" + image_path)
        
        image_index += 1
    
    print("Saved images")

    # create object with .json "header": maybe the paths of the images used, and the path for the output folder

    # header = {
    #     "output_folder_path": output_folder_path,
    #     "border_image_path": border_image_path,
    #     "border_color": border_color,
    #     "image_info": image_info,
    #     "search_right_to_left": search_right_to_left
    # }

    layer_names = [layer["name"] for layer in image_info]

    json_output = {
        "header": {
            "name": output_name,
            # "output_folder_path": output_folder_path,
            # "date_generated": date.today(),
            # "border_image_path": border_image_path,
            # "border_image_path": output_folder_path + "/border.png",
            "border_image_path": "border.png",
            "border_color": border_color,
            "layer_names": layer_names,
            "start_search_in_center": start_search_in_center,
            "search_right_to_left": search_right_to_left
        },
        "pose_objects": pose_objects,
        "images": images
    }
    
    json_filename = "/consistxels_pose_output_" + output_name + ".json"

    with open(output_folder_path + json_filename, 'w') as file:
        # json.dump(pose_object_array, file, indent=4)
        json.dump(json_output, file, indent=4)

    print("Saved .json output")

    border_image.save(output_folder_path + "/border.png") # TODO: WORK ON MORE. GET LOADING TO LOOK AT THIS INSTEAD!
    border_image.close()

    for layer_image in layer_images:
        layer_image.close()
    
    print("Success!")

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
def get_x_range(start = 0, end = 10, start_search_in_center = False, search_right_to_left = False): # for our purposes, assuming that width has NOT already been subtracted by two.
    # if start_search_in_center:
    #     width = end - start
    #     midpoint = math.ceil(float(width) / 2.0) + start
    #     if width % 2: midpoint -= 1

    #     if not search_right_to_left:
    #         return chain(range(midpoint, end - 2), range(start, midpoint))
    #     else:
    #         return chain(range(midpoint - 1, start - 1, -1), range(end - 3, midpoint - 1, -1))
    # else:
    #     if not search_right_to_left:
    #         return range(start, end - 2)
    #     else:
    #         return range(end - 3, start - 1, -1)
    if start_search_in_center:
        width = end - start
        midpoint = math.ceil(float(width) / 2.0) + start
        if width % 2: midpoint -= 1

        if not search_right_to_left:
            return chain(range(midpoint, end - 2), range(midpoint - 1, start - 1, -1))
        else:
            return chain(range(midpoint - 1, start - 1, -1), range(midpoint, end - 2))
    else:
        if not search_right_to_left:
            return range(start, end - 2)
        else:
            return range(end - 3, start - 1, -1)