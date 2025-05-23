from PIL import Image, ImageMorph, ImageColor, ImageDraw
import numpy as np
from numpy import asarray
from tkinter import filedialog
import json

# I probably should've split this into a few smaller functions. Oh well *shrug*
def GenerateJSON(border_image_path, border_color, image_info, search_right_to_left = True):

    border_image = Image.open(border_image_path) # get image

    border_image_array = asarray(border_image) # get image as array

    height, width = border_image_array.shape[:2] # get height and width of image

    # get border_color (needs to have an alpha channel)
    # border_color_rgb = ImageColor.getrgb("#00007fff")
    border_color_rgb = ImageColor.getrgb(border_color + "ff")

    # for testing
    # color_transparent = ImageColor.getrgb("#00000000")

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
    pose_object_array = []

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
        for x in (range(width - 2, 0, -1) if search_right_to_left else range(width - 2)): # columns

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
                    test_val_tuple = (found_pose_x, found_pose_y, endborder_x, endborder_y)

                    unbound_image = curr_layer_image.crop(test_val_tuple) # the full image inside the pose box

                    # the rectangle inside the image that actually contains a sprite - everything else is just transparent pixels
                    bbox = unbound_image.getbbox()
                    
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

                        # padding is saved for a few reasons. TODO: make better comment lmao
                        left_padding = bbox[0]
                        top_padding = bbox[1]
                        unbound_height, unbound_width = asarray(unbound_image).shape[:2]
                        bound_height, bound_width = asarray(bound_image).shape[:2]
                        right_padding = unbound_width - (left_padding + bound_width)
                        bottom_padding = unbound_height - (top_padding + bound_height)

                        if image_is_unique:
                            image_object_array.append({
                                "img": bound_image,
                                "left_padding": left_padding,
                                "top_padding": top_padding,
                                "right_padding": right_padding,
                                "bottom_padding": bottom_padding
                            })
                        else:
                            # this is where the setting would be to change from min padding to max padding
                            # currently, it's only min padding
                            # TODO: make that a setting. i think i deleted the other comment that i recommended the setting in
                            if image_object_array[image_index]["left_padding"] > left_padding:
                                image_object_array[image_index]["left_padding"] = left_padding
                            if image_object_array[image_index]["top_padding"] > top_padding:
                                image_object_array[image_index]["top_padding"] = top_padding
                            if image_object_array[image_index]["right_padding"] > right_padding:
                                image_object_array[image_index]["right_padding"] = right_padding
                            if image_object_array[image_index]["bottom_padding"] > bottom_padding:
                                image_object_array[image_index]["bottom_padding"] = bottom_padding

                        # either way, pose json stuff: how does each limb relate to the padding? etc

                        # do we need to store the padding for the originals as well??? well maybe not? idk, padding for the CURRENT thing is stored
                        # either way. so if it's not relative to other identical limb images, and is instead relative to corner, then that's fine.
                        # but that does NOT take into account the padding being updated as it goes - so maybe the saved padding should be stored
                        # somewhere, so it can work backwards for the unpadded size? though I guess we could just bbox again??? but that only works
                        # for completely unedited sprites

                        # so basically we'd need to update the saved offsets as we go, and that's not gonna happen. so need to figure out more
                        # automatic way

                        # sooooo I'm thinking we want to figure out the offset stuff later??? but like WHY though. let me think about this
                        # what i mean is: it may be best to go back & calculate each pose's offset later. but like, no, actually - it needs to
                        # be set now. but for the sake of the different padding, it's practically *necessary.* so i dunno! but at least the padding
                        # IS saved, and the image index CAN be traced to the padding pretty darn easily. idk i guess we can edit the offsets all at
                        # once later, AS LONG AS the offsets ARE determined HERE as well. and we can just add the appropriate padding then

                        limb_object = {
                            "name": curr_layer_name,
                            "x_offset": left_padding, # PRETTY SURE this is correct. these padding variables are unaltered, and have to do with the unbound image
                            "y_offset": top_padding,
                            "image_index": image_index,
                            "flip_h": is_flipped,
                            "rotation": rotation_amount
                        }

                        pose_object["limb_objects"].append(limb_object)

                        # and HERE'S where layer stuff stops mattering

                # some sort of dialog box that updates with what's currently going on, maybe? like a "Poses: ###"

                pose_object_array.append(pose_object)
                print("Poses found: " + str(len(pose_object_array)))

    # and then, here, we go through all poses, and all limbs, to update their padding according to the image index listed in the limb_object

    # print(json.dumps(pose_object_array, indent=4))
    
    with open(filedialog.asksaveasfilename(), 'w') as file:
        json.dump(pose_object_array, file, indent=4)

    border_image.close()

    for layer_image in layer_images:
        layer_image.close()



