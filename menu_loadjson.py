import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tooltip import ToolTip
from PIL import Image, ImageColor
import json
# from generate import adjust_offset_coordinates

class Menu_LoadJson(tk.Frame):
    def __init__(self, master, show_frame_callback):
        super().__init__(master)
        
        self.bg_color = "#2e2e2e"
        self.fg_color = "#ffffff"
        self.secondary_bg = "#3a3a3a"
        self.secondary_fg = "#6a6a6a"
        self.button_bg = "#444"
        self.field_bg = "#222222"

        self.separator_style = ttk.Style().configure("Custom.TSeparator", background=self.secondary_fg)

        self.color_transparent = ImageColor.getrgb("#00000000")

        self.configure(bg=self.bg_color)

        self.setup_ui(show_frame_callback)
    
    def setup_ui(self, show_frame_callback):
        self.top_frame = tk.Frame(self, bg=self.bg_color)
        self.top_frame.pack(fill="x", padx=10, pady=5)

        load_json_button = tk.Button(self.top_frame, text="Load JSON", command=self.load_json, bg=self.button_bg, fg=self.fg_color)
        load_json_button.pack(side="left", padx=5)
        ToolTip(load_json_button, "Load a valid JSON file.")

        self.loaded_json_label = tk.Label(self.top_frame, text="No .json loaded", bg=self.bg_color, fg=self.fg_color)
        self.loaded_json_label.pack(side="left", padx=5)

        ttk.Separator(self.top_frame, orient="vertical", style=self.separator_style).pack(fill="y", side="left", padx=5)

        # export stuff
        self.export_sheet_button = tk.Button(self.top_frame, text="Export Sprite Sheet", bg=self.button_bg, fg=self.fg_color, command=self.export_sprite_sheet, state="disabled")
        self.export_sheet_button.pack(side="left", padx=5)
        # self.export_sheet_button.
        ToolTip(self.export_sheet_button, "Export the entire sprite sheet.")

        ttk.Separator(self.top_frame, orient="vertical", style=self.separator_style).pack(fill="y", side="left", padx=5)

        # self.export_layer_optionmenu =         
        
        self.export_layer_button = tk.Button(self.top_frame, text="Export Individual Layer", bg=self.button_bg, fg=self.fg_color, command=self.export_layer, state="disabled")
        self.export_layer_button.pack(side="left", padx=5)
        ToolTip(self.export_layer_button, "Export one layer.")

        ttk.Separator(self.top_frame, orient="vertical", style=self.separator_style).pack(fill="y", side="left", padx=5)

        back_button = tk.Button(self.top_frame, text="Back to Main Menu", bg=self.button_bg, fg=self.fg_color, command=lambda: show_frame_callback("Main"))
        back_button.pack(side="right", padx=5)
        ToolTip(back_button, "...Come on, this one is self explanatory.", False, True, 2000)
    
    def load_json(self):
        path = filedialog.askopenfilename(filetypes=[("Json File", "*.json")]) # TODO: GO BACK AND ADD THIS TO OTHER FILE DIALOGS
        if path:
            # json_file = open(path)
            with open(path) as json_file:
                # json_data = json.load(json_file)
                self.json_data = json.load(json_file)
                json_file.close()

                self.output_folder_path = os.path.dirname(path)
                self.loaded_json_label.config(text=os.path.basename(path))
                
                # self.load_sprite_sheet(json_data, os.path.dirname(path))

                # TODO NEXT
                # get layer names
                # set them as the options in an OptionMenu
                # oh, by the way, also create the option menu
                # and figure out how to make buttons grayed-out / disabled
            
            # go to other menu
            # other menu displays json info, like header, etc
            # menu allows opening individual poses and selecting their layers/limbs & renaming them! (out of scope for now)
            # menu allows compiling all .png images and exporting either a single layer or the entire image!
            # - so there WILL need to be SOME layer management; could just have layer order be implicit, but, like... i dunno man

            # actually:
            # load json
            # some sort of layer view, as seen in other things
            # show other buttons: export individual layers, export full image, etc.

    def update_menu(self):
        pass

    # def load_sprite_sheet(self, json_data, output_folder_path): # add a bunch of checks for these images; do the files actually exist? etc.
    # def format_sprite_sheet(self, output_folder_path): # add a bunch of checks for these images; do the files actually exist? etc.
    def format_sprite_sheet(self): # add a bunch of checks for these images; do the files actually exist? etc.
        header = self.json_data["header"]
        # output_folder_path = header["output_folder_path"]
        # layer_info = header["layer_info"]
        layer_names = header["layer_names"]
        # pose_objects = self.json_data["pose_objects"]
        # images = self.json_data["images"]

        # border_image = Image.open(header["border_image_path"])

        with Image.open(self.output_folder_path + "/" + header["border_image_path"]) as border_image:
            sprite_sheet = border_image.copy()
            # border_image.close()

        # color_transparent = ImageColor.getrgb("#00000000")

        for i in range(len(layer_names) - 1, -1, -1): # WHY does it need to go to -1. that feels bad
            
            # # curr_layer_name = layer_info[i]["name"]
            # curr_layer_name = layer_names[i]
            # # print(curr_layer_name)
            # layer_image = Image.new("RGBA", sprite_sheet.size, self.color_transparent)

            # for pose in pose_objects:
            #     x_position = pose["x_position"]
            #     y_position = pose["y_position"]

            #     limb_objects = pose["limb_objects"]
            #     for limb in limb_objects:
            #         if limb["name"] == curr_layer_name: # does not work for images wherein different layers have the same name. either support this or prevent entirely
            #             # images[limb["image_index"]].open()

            #             x_offset = limb["x_offset"]
            #             y_offset = limb["y_offset"]

            #             with Image.open(output_folder_path + "/" + images[limb["image_index"]]) as limb_image:
            #                 adjusted_image = limb_image.copy()
            #                 rotate_type = None

            #                 # MIGHT be some wacky stuff with the offsets!
            #                 if limb["flip_h"]:
            #                     adjusted_image = adjusted_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

            #                 match limb["rotation"]:
            #                     case 1:
            #                         # limb_image = limb_image.transpose(Image.Transpose.ROTATE_270)# if not limb["flip_h"] else Image.Transpose.ROTATE_270)
            #                         rotate_type = Image.Transpose.ROTATE_90 if limb["flip_h"] else Image.Transpose.ROTATE_270
            #                         # rotate_type = Image.Transpose.ROTATE_270
            #                         # rotate_type = Image.Transpose.ROTATE_90
            #                     case 2:
            #                         # limb_image = limb_image.transpose(Image.Transpose.ROTATE_180)
            #                         rotate_type = Image.Transpose.ROTATE_180

            #                         # continue # !!! TODO
            #                     case 3:
            #                         # limb_image = limb_image.transpose(Image.Transpose.ROTATE_90)# if not limb["flip_h"] else Image.Transpose.ROTATE_90)
            #                         rotate_type = Image.Transpose.ROTATE_270 if limb["flip_h"] else Image.Transpose.ROTATE_90
            #                         # rotate_type = Image.Transpose.ROTATE_90
            #                         # rotate_type = Image.Transpose.ROTATE_270
            #                     # case _:
            #                         # continue # !!! TODO

            #                 if rotate_type:
            #                     adjusted_image = adjusted_image.transpose(rotate_type)

                            # x_offset_adjust, y_offset_adjust = x_offset + x_position, y_position + y_offset
            #                 # if rotate_type or limb["flip_h"]:
            #                 #     bound_original_image = limb_image.crop(limb_image.getbbox())
            #                 #     bound_adjusted_image = adjusted_image.crop(adjusted_image.getbbox())

            #                 #     # x_offset_adjust, y_offset_adjust = adjust_offset_coordinates(x_offset_adjust, y_offset_adjust, bound_original_image.width, bound_original_image.height, bound_adjusted_image.width, bound_adjusted_image.height, rotate_type, limb["flip_h"])
            #                 #     x_offset_adjust, y_offset_adjust = adjust_offset_coordinates(x_offset_adjust, y_offset_adjust, bound_original_image.width, bound_original_image.height, bound_adjusted_image.width, bound_adjusted_image.height, rotate_type)

            #                 # layer_image.paste(limb_image, (x_position + x_offset, y_position + y_offset))
            #                 layer_image.paste(adjusted_image, (x_offset_adjust, y_offset_adjust))
                            
            # adjusted_image, x_offset_adjust, y_offset_adjust = self.load_layer(json_data, layer_image, i, output_folder_path)
            # layer_image.paste(adjusted_image, (x_offset_adjust, y_offset_adjust))
            
            # sprite_sheet.paste(layer_image)
            sprite_sheet = Image.alpha_composite(sprite_sheet, self.format_layer(i))
        
        # sprite_sheet.show()
        return sprite_sheet

    # def export_sprite_sheet(self, path):
    def export_sprite_sheet(self):
        sprite_sheet_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")], initialfile= "export_" + self.json_data["header"]["name"] + "_full.png")
        # sprite_sheet = self.format_sprite_sheet(os.path.dirname(path))
        # sprite_sheet.save(sprite_sheet_path)
        self.format_sprite_sheet().save(sprite_sheet_path)

    # def load_layer(self, layer_info, layer_index, width, height, pose_objects):
    #     layer_image = Image.new("RGBA", (width, height), self.color_transparent)
    #     curr_layer_name = layer_info[layer_index]["name"]

    #     for pose in pose_objects:
    #         x_position = pose["x_position"]
    #         y_position = pose["y_position"]

    #         limb_objects = pose["limb_objects"]
    #         for limb in limb_objects:
    #             if limb["name"] == curr_layer_name: # does not work for images wherein different layers have the same name. either support this or prevent entirely
    #                 # images[limb["image_index"]].open()

    #                 with images[limb["image_index"]].open() as limb_image:
    #                     x_offset = limb["x_offset"]
    #                     y_offset = limb["y_offset"]
    #                     layer_image.paste(limb_image, (x_position + x_offset, y_position + y_offset))
            
    #     return layer_image

    # def load_layer(self, json_data, size, layer_index, output_folder_path): # technically could just use json_data to find size
    def format_layer(self, layer_index): # technically could just use json_data to find size
        
        # output_folder_path = json_data["header"][""]
        pose_objects = self.json_data["pose_objects"]
        layer_names = self.json_data["header"]["layer_names"]
        curr_layer_name = layer_names[layer_index]
        images = self.json_data["images"]

        with Image.open(self.output_folder_path + "/" + self.json_data["header"]["border_image_path"]) as border_image:
            size = border_image.size # might be worth saving the size as a property of self?

        layer_image = Image.new("RGBA", size, self.color_transparent)

        for pose in pose_objects:
            x_position = pose["x_position"]
            y_position = pose["y_position"]

            limb_objects = pose["limb_objects"]
            for limb in limb_objects:
                if limb["name"] == curr_layer_name: # does not work for images wherein different layers have the same name. either support this or prevent entirely

                    x_offset = limb["x_offset"]
                    y_offset = limb["y_offset"]

                    with Image.open(self.output_folder_path + "/" + images[limb["image_index"]]) as limb_image:
                        adjusted_image = limb_image.copy()
                        rotate_type = None

                        if limb["flip_h"]:
                            adjusted_image = adjusted_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

                        match limb["rotation"]:
                            case 1:
                                rotate_type = Image.Transpose.ROTATE_90 if limb["flip_h"] else Image.Transpose.ROTATE_270
                            case 2:
                                rotate_type = Image.Transpose.ROTATE_180
                            case 3:
                                rotate_type = Image.Transpose.ROTATE_270 if limb["flip_h"] else Image.Transpose.ROTATE_90

                        if rotate_type:
                            adjusted_image = adjusted_image.transpose(rotate_type)

                        x_offset_adjust, y_offset_adjust = x_offset + x_position, y_position + y_offset
                        layer_image.paste(adjusted_image, (x_offset_adjust, y_offset_adjust))
                        # return adjusted_image, x_offset_adjust, y_offset_adjust
        
        return layer_image

    def export_layer(self):
        layer_index = 0
        layer_name = self.json_data["header"]["layer_names"][layer_index] # or, rather than using layername, could use string inside optionmenu?
        layer_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")], initialfile= "export_" + self.json_data["header"]["name"] + "_" + layer_name + ".png")
        self.format_layer(layer_index).save(layer_path)

# def adjust_offset_coordinates(
#     x: int,
#     y: int,
#     orig_w: int,
#     orig_h: int,
#     new_w: int,
#     new_h: int,
#     rotation=None,
#     # flip_h=False
# ):
#     """
#     Adjusts paste coordinates for a rotated (and possibly flipped) image.

#     Parameters:
#         x, y: Original top-left paste coordinates
#         orig_w, orig_h: Original size before rotation
#         new_w, new_h: Size after rotation
#         rotation: Image.ROTATE_90, ROTATE_180, ROTATE_270, or None
#         flip_h: Whether the image was flipped horizontally

#     Returns:
#         (adjusted_x, adjusted_y)
#     """

#     # Horizontal flip adjustment
#     # if flip_h:
#     #     x = x + (orig_w - 1) - 2 * (x % orig_w)
        
#     # Rotation adjustment
#     if rotation == Image.ROTATE_90:
#         x += orig_h - new_w
#         if orig_w % 2 != orig_h % 2:
#             x += 1 if orig_h % 2 == 0 else 0
#             y -= 1 if orig_w % 2 == 0 else 0
#             # x += 1
#             # y += -1
#             # x += 0 if orig_h % 2 == 0 else 1
#             # y -= 0 if orig_w % 2 == 0 else 1

#     elif rotation == Image.ROTATE_180:
#         x += orig_w - new_w
#         y += orig_h - new_h
#         if orig_w % 2 != orig_h % 2:
#             x += 1 if orig_w % 2 == 0 else 0
#             y -= 1 if orig_h % 2 == 0 else 0
#             # x += 1
#             # y -= 1
#             # x += 0 if orig_w % 2 == 0 else 1
#             # y -= 0 if orig_h % 2 == 0 else 1

#     elif rotation == Image.ROTATE_270:
#         y += orig_w - new_h
#         if orig_w % 2 != orig_h % 2:
#             x -= 1 if orig_h % 2 == 0 else 0
#             y += 1 if orig_w % 2 == 0 else 0
#             # x += -1
#             # y += 1
#             # x -= 0 if orig_h % 2 == 0 else 1
#             # y += 0 if orig_w % 2 == 0 else 1

#     return x, y








### TODO TODO TODO: TRYING TO SEPARATE EXPORTING LAYERS AND THE ENTIRE IMAGE INTO FUNCTIONS, SO THAT THEY CAN BE SEPARATE OPTIONS!