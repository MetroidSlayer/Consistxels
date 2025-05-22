from PIL import Image, ImageTk, ImageOps

def GenerateJSON(border_image, border_color, image_info):
    print("got to generate.py GenerateJSON()")
    print(border_image)
    print(border_color)
    print("got to loop")
    for info in image_info:
        print("loopstart")
        print(info["path"])
        print(info["name"])
        print("loopend")
    print("got past loop")


