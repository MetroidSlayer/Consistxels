from PIL import Image, ImageMorph, ImageColor, ImageDraw
import numpy as np
from numpy import asarray
from tkinter import filedialog
import json

# TODO: ABSOLUTELY CRITICAL!!! make sure everything is flipped, according to search_right_to_left
# no longer doin it that way, dont worry abt it :)

def GenerateJSON(border_image_path, border_color, image_info, search_right_to_left = True):
    # print("got to generate.py GenerateJSON()")
    # print(border_image)
    # print(border_color)
    # print("got to loop")
    # for info in image_info:
    #     print("loopstart")
    #     print(info["path"])
    #     print(info["name"])
    #     print("loopend")
    # print("got past loop")


    
    # get image as array
    border_image = Image.open(border_image_path)


    test_curr_layer_image = Image.open(image_info[0]["path"])

    # if search_right_to_left:
    #     border_image = border_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

    border_image_array = asarray(border_image)

    # for y in border_image_array.size:
    #     for x in border_image_array[y].size:

    height, width = border_image_array.shape[:2]

    # test_bordercounter = 0
    # test_falsepositives = 0

    # test_outputimg = border_image.copy()
    # test_outputimg = Image.new("RGBA", (width, height), ImageColor.getrgb("#00000000"))

    # border_color_rgb = ImageColor.getcolor(border_color, "rgba")
    # border_color_rgba = (border_color_rgb[0], border_color_rgb[1], border_color_rgb[2], 255)

    border_color_rgb = ImageColor.getrgb("#00007fff")

    # color_transparent = ImageColor.getrgb("#00000000")

    # for storing unique images!
    # specifically, will store the image, and its minimum padding (make min or max padding a setting? just min for now i guess)
    # format: [{"img", "left_padding", "top_padding", "right_padding", "bottom_padding"}]
    image_object_array = []

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

    # and for good measure, limb_objects format:
    # [{"x_offset", "y_offset", "image_index", "flip_h", "rotation"}]
    # this is specifically limbs that are PART OF a pose, not just saved limb images. so these contain pose-specific data, and are not interchangeable,
    # even if they reference the same limb image.
    # also, the image they reference is gonna be a number - and that'll reference the number of images, i think??? like, there are 99 images in
    # a given images folder, and the number can just double as the filename
    # also also, "offset" is referring to how far off the top-left corner of the sprite is from the top-left corner of the pose box.
    # also also also, "flip_h" does what it says on the tin (it's a bool), and "rotation" stores an int, and increments rotation by 90 degrees

    # (might as well subtract 2 because there is no pose that can fit in a 2-wide or 2-high box, inclusive of border - there's no space)
    for y in range(height - 2):      # rows
        for x in (range(width - 2, 0, -1) if search_right_to_left else range(width - 2)):   # columns

            # pixel = border_image_array[y, x]
            pixel = border_image.getpixel([x,y])
            endborder_x = -1
            endborder_y = -1

            # if pixel[0] == border_color_rgb[0] and pixel[1] == border_color_rgb[1] and pixel[2] == border_color_rgb[2]:
            if pixel == border_color_rgb:
                # pass
                # test_bordercounter += 1

                if border_image.getpixel([x + 1, y]) == border_color_rgb \
                and border_image.getpixel([x, y + 1]) == border_color_rgb \
                and not border_image.getpixel([x + 1, y + 1]) == border_color_rgb:
                    pass
                    # test_bordercounter += 1

                    

                    # iterate all the way to the right. if no border is found, it's not a pose box after all.
                    for x2 in range(x + 1, width):
                        if border_image.getpixel([x2, y + 1]) == border_color_rgb:
                            endborder_x = x2
                            break
                    
                    # if a border has been found, it's likely a pose box.
                    if endborder_x != -1:
                        

                        # look for the bottom right of the pose box.
                        for y2 in range(y + 1, height):
                            # print(endborder_x)
                            # print(y2)
                            pixel2 = border_image.getpixel([endborder_x, y2])

                            # if a non-border pixel's ever found, it's not a pose box.
                            if pixel2 != border_color_rgb:
                                # test_falsepositives += 1
                                break
                            
                            if border_image.getpixel([endborder_x - 1, y2]) == border_color_rgb \
                            and border_image.getpixel([endborder_x, y2 - 1]) == border_color_rgb \
                            and not border_image.getpixel([endborder_x - 1, y2 - 1]) == border_color_rgb:
                                #pose box found!
                                # test_bordercounter += 1
                                endborder_y = y2

                                # print("posebox width: " + str(endborder_x - x))
                                # print("posebox height: " + str(endborder_y - y))
                                # print("posebox x: " + str(x))
                                # print("posebox y: " + str(y))

                                break
                    # else:
                        # test_falsepositives += 1
        
            if endborder_x >= 0 and endborder_y >= 0:

                # match test_bordercounter % 6:
                #     case 0:
                #         colorstring = "red"
                #     case 1:
                #         colorstring = "orange"
                #     case 2:
                #         colorstring = "yellow"
                #     case 3:
                #         colorstring = "green"
                #     case 4:
                #         colorstring = "blue"
                #     case 5:
                #         colorstring = "purple"
                
                # test_bordercounter += 1

                # draw = ImageDraw.Draw(test_outputimg)
                # draw.rectangle([x, y, endborder_x,endborder_y], ImageColor.getrgb(colorstring), ImageColor.getrgb("#00007f"))
                
                # pass

                # when found, grab total size of this new pose we've found
                #   new pose, so:
                #   - create pose data, position, etc.
                #   - add to json
                # -- well HOLD ON. no need to create a pose if there's nothing in the pose box. so do that first.
                # pose_dict = {}

                # pose_dict["name"] = ""

                # after verifying pose box, get image in box
                # if no image in box, move on
                # if image in box, get bounding box

                # TODO: due to the way Image.open() works, ALL LAYER IMAGES ought to be opened at the start, alongside the border image
                # test_curr_layer_image = Image.open(image_info[0]["path"])
                test_curr_layer_name = image_info[0]["name"]
                
                # test_curr_layer_image.show()
                # print(test_curr_layer_name)
                # return

                # SO, we have our pose box. That means we KNOW there's a pose here. I'm going to choose to save even completely empty poses;
                # that way, it's gonna be less confusing for me, I think.

                found_pose_x = x + 1
                found_pose_y = y + 1
                found_pose_width = endborder_x - x - 1
                found_pose_height = endborder_y - y - 1

                pose_object = {
                    "name": "idk", #something to do with the position, methinks
                    "x_position": found_pose_x,
                    "y_position": found_pose_y,
                    "width": found_pose_width,
                    "height": found_pose_height,
                    "limb_objects": []
                }
                
                
                # unbound_image = Image.new("RGBA", (found_pose_width, found_pose_height), color_transparent)
                # unbound_image.paste(test_curr_layer_image, (found_pose_x, found_pose_y, found_pose_width, found_pose_height))
                # unbound_image.show()
                # return

                # crop parameter tuple: (left, top, right, bottom)
                test_val_tuple = (found_pose_x, found_pose_y, endborder_x, endborder_y)

                unbound_image = test_curr_layer_image.crop(test_val_tuple)
                # unbound_image.show()
                # return

                bbox = unbound_image.getbbox()
                
                if bbox:
                    # TODO: if bbox, then there IS a pose here!!! and new stored pose info needs to be stored, so that duplicate limbs can
                    # be linked to old ones, etc. Lots of reasons to do stuff here. That said, are we checking if every layer has a bbox?
                    # Are we storing EMPTY pose data for found pose boxes, even if completely empty? maybe idk
                    
                    # store info implied by bounding box - i.e. offset. this is for formatting purposes in export, BUT ALSO for deciding maximum bounds for each limb
                    

                    # crop image down to bounding box
                    bound_image = unbound_image.crop(bbox)
                    # bound_image.show()
                    # return

                    # bound_image_array = asarray(bound_image) # can probably get rid of, and replace with a basic asarray() later when it's used
                    
                    image_is_unique = True
                    image_index = 0 # will setting this to 0 cause problems? probably not, right???

                    # for posed limbs
                    is_flipped = False
                    rotation_amount = 0 # increment by 1, each represents 90 degrees

                    # HEY BOZO! remember, still have no idea if .transpose(ROTATE) rotates the bounds, or if we gotta do wacky stuff

                    # check against stored images - check w/ flip_h, flip_y, & rotate. so like 12 checks per limb :(
                    for data in image_object_array:
                        img = data["img"]
                        # img_array = asarray(img)

                        # if bound_image_array == img_array: # the bound image is already stored; move on
                        if bound_image.tobytes() == img.tobytes(): # the bound image is already stored; move on
                            image_is_unique = False
                            break
                        
                        # prepare a flipped version of the img, since it'll commonly be an already-stored img, and it's in a lotta checks
                        flip_h = bound_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                        
                        # if asarray(flip_h) == img_array: # the flipped image is already stored; move on
                        if flip_h.tobytes() == img.tobytes(): # the flipped image is already stored; move on
                            image_is_unique = False
                            is_flipped = True
                            break
                        
                        # rotate normal image 90 degrees
                        # if asarray(bound_image.transpose(Image.Transpose.ROTATE_90)) == img_array:
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

                    # left padding: bbox left
                    left_padding = bbox[0]

                    # top padding: bbox top
                    top_padding = bbox[1]

                    unbound_height, unbound_width = asarray(unbound_image).shape[:2]
                    # bound_height, bound_width = bound_image_array.shape[:2]
                    bound_height, bound_width = asarray(bound_image).shape[:2]

                    # right padding: unbound width - (bbox left + bound width)
                    right_padding = unbound_width - (left_padding + bound_width)

                    # bottom padding: unbound height - (bbox top + bound height)
                    bottom_padding = unbound_height - (top_padding + bound_height)

                    if image_is_unique:
                        image_object_array.append({
                            "img": bound_image,
                            "left_padding": left_padding,
                            "top_padding": top_padding,
                            "right_padding": right_padding,
                            "bottom_padding": bottom_padding
                        })
                        # stored_image_array[image_index]["img"] = bound_image
                        # stored_image_array[image_index]["left_padding"] = left_padding
                        # stored_image_array[image_index]["top_padding"] = top_padding
                        # stored_image_array[image_index]["right_padding"] = right_padding
                        # stored_image_array[image_index]["bottom_padding"] = bottom_padding
                    else:
                        # this is where the setting would be to change from min padding to max padding
                        # currently, it's only min padding
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

                    # test val in there until we do ALL the layer stuff
                    limb_object = {
                        "name": test_curr_layer_name,
                        "x_offset": 0,
                        "y_offset": 0,
                        "image_index": image_index,
                        "flip_h": is_flipped,
                        "rotation": rotation_amount
                    }

                    pose_object["limb_objects"].append(limb_object)

                    # and HERE'S where layer stuff stops mattering

                    pose_object_array.append(pose_object)










                        
                # else:
                #     pass # no image; move on

                # test_paste_tuple = (found_pose_x, found_pose_y, found_pose_width, found_pose_height)
                
                # unbound_image = Image.new("RGBA", (found_pose_width, found_pose_height), color_transparent)
                # unbound_image.paste(test_curr_layer_image, test_paste_tuple)


                
                # if no match is found:
                # - create new limb json
                # - save limb img? MAYBE? idk. at least hold onto it

                # create new posed_limb json
                # store position of offset (if new, no offset at all)
                # compare new offset to old img size: if bigger, or maybe smaller i haven't decided yet, change size of img accordingly
                # reference limb img in posed_limb
                # go to pose json and add data, from layer name, that references this posed_limb data 

                # loop to start of comment pseudocode



                
                

        #     if test_bordercounter > 0: break
        # if test_bordercounter > 0: break

    print(json.dumps(pose_object_array, indent=4))

    # print("found poseboxes: " +  str(test_bordercounter))
    # print("false positives: " + str(test_falsepositives))

    # test_outputimg.show()
    # test_outputimg.save(filedialog.asksaveasfilename())




    # mask_tuple = (0, 0, 0, 0)

    # corner_image = Image.new("RGBA", [2,2], border_color)
    # corner_image.putpixel([1,1], mask_tuple)
    # corner_image.show()



    # search for pose
    # - iterate until find border pixel
    # - check if border pixel is topleft corner
    #   - iterate until find right bounds
    #   - if found, iterate until find EITHER bottomleft corner OR a pixel other than border pixel

    border_image.close()
    test_curr_layer_image.close()


