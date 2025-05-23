from PIL import Image, ImageMorph, ImageColor, ImageDraw
import numpy as np
from numpy import asarray
from tkinter import filedialog

# TODO: ABSOLUTELY CRITICAL!!! make sure everything is flipped, according to search_right_to_left

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
                
                pass

                # when found, grab total size of this new pose we've found
                #   new pose, so:
                #   - create pose data, position, etc.
                #   - add to json
                # pose_dict = {}

                # pose_dict[""]

                # after verifying pose box, get image in box
                # if no image in box, move on
                # if image in box, get bounding box

                # store info implied by bounding box - i.e. offset. this is for formatting purposes in export, BUT ALSO for deciding maximum bounds for each limb
                # crop image down to bounding box
                # check against stored images - check w/ flip_h, flip_y, & rotate. so like 12 checks per limb :(
                
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


