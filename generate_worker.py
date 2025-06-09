import sys
import json
import os
import generate

# import tkinter as tk
# from tkinter import filedialog

# import threading

# from datetime import datetime

def main():
    # start_time = datetime.now() # Time taken to generate is tracked and shown at the end

    # print("got to generate_worker.main()")
    if len(sys.argv) < 2:
        print("Missing argument", file=sys.stderr, flush=True)
        sys.exit(1)

    temp_json_path = sys.argv[1]
    if not os.path.exists(temp_json_path):
        print("Temporary .json data does not exist", file=sys.stderr, flush=True)
        sys.exit(1)

    with open(temp_json_path, 'r') as f:
        temp_json_data = json.load(f)

    os.remove(temp_json_path)

    data = temp_json_data.get("data", {})
    path = temp_json_data.get("path", "")


    # header = {
    #         "name": "test",
    #         "consistxels_version": "test",
    #         "paths_are_local": True, # CHANGE! Or i guess not HERE, this only really applies to saved layer data and all that
    #         "width": None, # get this figured out sooner probably?
    #         "height": None # get this figured out sooner probably?
    # }

    # search_data = {
    #         "start_search_in_center": True,
    #         "search_right_to_left": False,
    #         "detect_identical_images": True, # TODO
    #         "detect_rotated_images": True, # TODO
    #         "detect_flip_h_images": True, # TODO
    #         "detect_flip_v_images": False # TODO
    #     }

    # search_type_data = {
    #         "search_type": "Border",
    #         "border_color": "#00007f",
    #         "spacing_rows": "0", # TODO: change so can only be int
    #         "spacing_columns":  "0", # TODO: change so can only be int
    #         "spacing_outer_padding":  "0", # TODO: change so can only be int
    #         "spacing_inner_padding":  "0", # TODO: change so can only be int
    #         "spacing_x_separation":  "0", # TODO: change so can only be int
    #         "spacing_y_separation":  "0" # TODO: change so can only be int
    #     }

    # generation_data = {
    #         "automatic_padding_type": "None", # TODO: change so can only be int
    #         "custom_padding_amount": 10, # TODO: change so can only be int
    #         "generate_empty_poses": False # TODO
    #     }

    #     # TODO: A LOT
    # layer_data = []
    #     # duplicate_layer_name = False
    #     # for layer in self.layer_data:
    #         # if layer["name"] in [image["name"] for image in layer_data]:
    #             # duplicate_layer_name = True
    #             # break
    #         # layer_data.append({"path": layer["path"], "name": layer["name"], "alt_source": layer["alt_source"]})
    # layer_data.append({ # TODO TODO TODO
    #             "name": "test", "is_border": False, "is_cosmetic_only": False,
    #             "search_image_path": "C:/Users/metro/Files/SpriteSomething-1.70-windows/exports/dread metroid suit/consistxels/new_generatepy_test/closearm_search_image.png", "source_image_path": "C:/Users/metro/Files/SpriteSomething-1.70-windows/exports/dread metroid suit/consistxels/new_generatepy_test/closearm_source_image.png",
    #             "export_original_images": True
    #         })
    
    # layer_data.append({ # TODO TODO TODO
    #             "name": "test", "is_border": False, "is_cosmetic_only": False,
    #             "search_image_path": "C:/Users/metro/Files/SpriteSomething-1.70-windows/exports/dread metroid suit/consistxels/new_generatepy_test/closeleg_search_image.png", "source_image_path": "C:/Users/metro/Files/SpriteSomething-1.70-windows/exports/dread metroid suit/consistxels/new_generatepy_test/closeleg_source_image.png",
    #             "export_original_images": True
    #         })
    
    # layer_data.append({ # TODO TODO TODO
    #             "name": "test", "is_border": False, "is_cosmetic_only": False,
    #             "search_image_path": "C:/Users/metro/Files/SpriteSomething-1.70-windows/exports/dread metroid suit/consistxels/new_generatepy_test/upperbody_search_image.png", "source_image_path": "C:/Users/metro/Files/SpriteSomething-1.70-windows/exports/dread metroid suit/consistxels/new_generatepy_test/upperbody_source_image.png",
    #             "export_original_images": True
    #         })
    
    # layer_data.append({ # TODO TODO TODO
    #             "name": "test", "is_border": False, "is_cosmetic_only": False,
    #             "search_image_path": "C:/Users/metro/Files/SpriteSomething-1.70-windows/exports/dread metroid suit/consistxels/new_generatepy_test/farleg_search_image.png", "source_image_path": "C:/Users/metro/Files/SpriteSomething-1.70-windows/exports/dread metroid suit/consistxels/new_generatepy_test/farleg_source_image.png",
    #             "export_original_images": True
    #         })
    
    # layer_data.append({ # TODO TODO TODO
    #             "name": "test", "is_border": False, "is_cosmetic_only": False,
    #             "search_image_path": "C:/Users/metro/Files/SpriteSomething-1.70-windows/exports/dread metroid suit/consistxels/new_generatepy_test/fararm_search_image.png", "source_image_path": "C:/Users/metro/Files/SpriteSomething-1.70-windows/exports/dread metroid suit/consistxels/new_generatepy_test/fararm_source_image.png",
    #             "export_original_images": True
    #         })

    # if search_type_data["search_type"] == "Border": # TODO. can mostly just copy-and-paste this. still do want rigid control of the data in the border layer
    #         layer_data.append({
    #             "name": "border", "is_border": True, "is_cosmetic_only": True,
    #             "search_image_path": "C:/Users/metro/Files/SpriteSomething-1.70-windows/exports/dread metroid suit/consistxels/new_generatepy_test/border.png", "source_image_path": None,
    #             "export_original_images": True
                
    #         })

    # pose_data = None
    #     # if self.search_type_option.get() == "Preset":
    #         # pass # TODO
        
    # data = {
    #         "header": header, "search_data": search_data, "search_type_data": search_type_data,
    #         "generation_data": generation_data, "layer_data": layer_data, "pose_data": pose_data
    #     }
    
    # path = "C:/Users/metro/Files/SpriteSomething-1.70-windows/exports/dread metroid suit/consistxels/newtest"

    # root = tk.Tk()
    # popup = tk.Toplevel(root)
    # popup.attributes("-topmost", True)
    # tk.Label(popup, text="test").pack()

    # app(root, data, path).pack()

    # root.mainloop()

    generate.generate_all(data, path)

    # end_time = datetime.now()
    # time_elapsed = end_time - start_time
    # time_elapsed_seconds = int(time_elapsed.total_seconds())
    # hours = time_elapsed_seconds // 3600
    # minutes = (time_elapsed_seconds % 3600) // 60
    # seconds = time_elapsed_seconds % 60
    # formatted_time_elapsed = f"{hours:02}:{minutes:02}:{seconds:02}"
    # print(formatted_time_elapsed)

    # input("Done! Press Enter to exit...")

# class app(tk.Frame):
    # def __init__(self, root, data, path):
    #     # generate.generate_all(data, path)
        
        
    #     threading.Thread(target=generate.generate_all, args=[data, path], daemon=True).start()

    #     popup = tk.Toplevel()
    #     popup.attributes("-topmost", True)
    #     # generate.generate_all(data, path)

if __name__ == "__main__":
    main()