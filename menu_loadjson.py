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

        # ttk.Separator(self.top_frame, orient="vertical", style=self.separator_style).pack(fill="y", side="left", padx=5)


        
        self.mid_frame = tk.Frame(self, bg=self.bg_color)
        # self.mid_frame.pack(fill="x", padx=10, pady=5)
        self.mid_frame.pack(side="left", fill="y", padx=10)


        # other options
        # self.include_border = tk.BooleanVar()
        # include_border_checkbutton = tk.Checkbutton(self.mid_frame, text="Include border in export", bg=self.bg_color, fg=self.fg_color, selectcolor=self.button_bg, onvalue=True, offvalue=False, variable=self.include_border)
        # include_border_checkbutton.select()
        # # include_border_checkbutton.pack(side="left", padx=5)
        # include_border_checkbutton.grid(row=0, column=0, sticky="w")
        # ToolTip(include_border_checkbutton, "In exported images, include the border.\n(Recommended for full sprite sheet exports)")
        # # could instead have an optionmenu where it's, like, "above", "below", "none" in case the position of the border matters

        # export stuff
        self.export_sheet_button = tk.Button(self.mid_frame, text="Export Sprite Sheet Image", bg=self.button_bg, fg=self.fg_color, command=self.export_sprite_sheet, state="disabled")
        # self.export_sheet_button.pack(padx=5)
        self.export_sheet_button.grid(row=1, column=0, sticky="w")
        ToolTip(self.export_sheet_button, "Export the entire sprite sheet as a single image.")

        # ttk.Separator(self.mid_frame, orient="vertical", style=self.separator_style).pack(fill="y", side="left", padx=5)
 
        
        self.export_layer_button = tk.Button(self.mid_frame, text="Export Individual Layer Image", bg=self.button_bg, fg=self.fg_color, command=self.export_layer, state="disabled")
        # self.export_layer_button.pack(padx=5)
        self.export_layer_button.grid(row=2, column=0, sticky="w")
        ToolTip(self.export_layer_button, "Export one layer as an image.")
        
        self.layer_option = tk.StringVar()
        self.layer_option.set("")
        self.export_layer_optionmenu = tk.OptionMenu(self.mid_frame, self.layer_option, "")

        
        self.export_layer_optionmenu.configure(bg=self.bg_color, fg=self.fg_color, activebackground=self.secondary_bg, activeforeground=self.fg_color, width=28, anchor="w", justify="left", state="disabled")
        self.export_layer_optionmenu["menu"].configure(bg=self.field_bg, fg=self.fg_color, activebackground=self.secondary_bg, activeforeground=self.fg_color)

        # self.export_layer_optionmenu.pack(side="left", padx=5)
        self.export_layer_optionmenu.grid(row=2, column=1, sticky="w")
        ToolTip(self.export_layer_optionmenu, "Choose which layer to export.")





        # ttk.Separator(self.mid_frame, orient="vertical", style=self.separator_style).pack(fill="y", side="left", padx=5)




        back_button = tk.Button(self.top_frame, text="Back to Main Menu", bg=self.button_bg, fg=self.fg_color, command=lambda: show_frame_callback("Main"))
        back_button.pack(side="right", padx=5)
        ToolTip(back_button, "...Come on, this one is self explanatory.", False, True, 2000)
    
    def load_json(self):
        path = filedialog.askopenfilename(filetypes=[("Json File", "*.json")]) # TODO: GO BACK AND ADD THIS TO OTHER FILE DIALOGS
        if path:
            # json_file = open(path)
            with open(path) as json_file:
                # json_data = json.load(json_file)
                self.json_data = json.load(json_file) #could unindent after this?
                # json_file.close()

                self.output_folder_path = os.path.dirname(path)
                self.loaded_json_label.config(text=os.path.basename(path) + " (" + self.json_data["header"]["name"] + ")")

                self.export_sheet_button.configure(state="normal")
                self.export_layer_button.configure(state="normal")

                self.export_layer_optionmenu.configure(state="normal")
                menu = self.export_layer_optionmenu["menu"]
                menu.delete(0, "end")

                # for layer_name in self.json_data["header"]["layer_names"]:
                # self.image_size = (-1,-1)
                self.image_size = (self.json_data["header"]["width"], self.json_data["header"]["height"])

                # for layer in self.json_data["layer_data"]:
                #     menu.add_command(label=layer["name"], command=lambda value=layer["name"]: self.layer_option.set(value))

                #     if self.image_size == (-1,-1):
                #         if layer["search_image_path"]:
                #             with Image.open(layer["search_image_path"]) as img:
                #                 self.image_size = img.size
                #         elif layer["source_image_path"]:
                #             with Image.open(layer["source_image_path"]) as img:
                #                 self.image_size = img.size
                
                # if self.json_data["header"]["layer_names"]:
                if self.json_data["layer_data"]:
                    # self.layer_option.set(self.json_data["header"]["layer_names"][0])
                    self.layer_option.set(self.json_data["layer_data"][0]["name"])
                else:
                    self.layer_option.set("")
                
                # think of some equivalent?
                # with Image.open(self.output_folder_path + "/" + self.json_data["header"]["border_image_path"]) as border_image:
                    # self.image_size = border_image.size

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
        # layer_names = header["layer_names"]
        layer_data = self.json_data["layer_data"]
        # pose_objects = self.json_data["pose_objects"]
        # images = self.json_data["images"]

        # border_image = Image.open(header["border_image_path"])

        # with Image.open(self.output_folder_path + "/" + header["border_image_path"]) as border_image:
        #     sprite_sheet = border_image.copy()
        #     # border_image.close()

        # with Image.open(self.output_folder_path + "/" + self.json_data["header"]["border_image_path"]) as border_image:
        #     size = border_image.size # might be worth saving the size as a property of self?

        sprite_sheet = Image.new("RGBA", self.image_size, self.color_transparent)

        # color_transparent = ImageColor.getrgb("#00000000")

        # for i in range(len(layer_names) - 1, -1, -1): # WHY does it need to go to -1. that feels bad
        for i in range(len(layer_data) - 1, -1, -1): # WHY does it need to go to -1. that feels bad
            
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
            # print("Layer " + layer_names[i] + " formatted")
            print(f"Layer {layer_data[i]['name']} formatted")
        
        # sprite_sheet.show()
        print("Success")
        return sprite_sheet

    # def export_sprite_sheet(self, path):
    def export_sprite_sheet(self):
        sprite_sheet_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")], initialfile= "export_" + self.json_data["header"]["name"] + "_full.png")
        # sprite_sheet = self.format_sprite_sheet(os.path.dirname(path))
        # sprite_sheet.save(sprite_sheet_path)

        if sprite_sheet_path:
            sprite_sheet_image = self.format_sprite_sheet()

            # if (self.include_border.get()):
                # with Image.open(self.output_folder_path + "/" + self.json_data["header"]["border_image_path"]) as border_image:
                    # sprite_sheet_image = Image.alpha_composite(sprite_sheet_image, border_image)

            # self.format_sprite_sheet().save(sprite_sheet_path)
            sprite_sheet_image.save(sprite_sheet_path)

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
        # pose_objects = self.json_data["pose_objects"]
        pose_data = self.json_data["pose_data"]
        # layer_names = self.json_data["header"]["layer_names"]
        layer_data = self.json_data["layer_data"]
        curr_layer_name = layer_data[layer_index]["name"]
        layer = layer_data[layer_index]

        layer_image = None

        if not layer["is_border"] and not layer["is_cosmetic_only"]:

            # images = self.json_data["images"]
            image_data = self.json_data["image_data"]

            # with Image.open(self.output_folder_path + "/" + self.json_data["header"]["border_image_path"]) as border_image:
            #     size = border_image.size # might be worth saving the size as a property of self?

            layer_image = Image.new("RGBA", self.image_size, self.color_transparent)

            # for pose in pose_objects:
            for pose in pose_data:
                x_position = pose["x_position"]
                y_position = pose["y_position"]

                # limb_objects = pose["limb_objects"]
                limb_data = pose["limb_data"]
                for limb in limb_data:
                    if limb["name"] == curr_layer_name: # does not work for images wherein different layers have the same name. either support this or prevent entirely

                        x_offset = limb["x_offset"]
                        y_offset = limb["y_offset"]

                        # with Image.open(self.output_folder_path + "/" + images[limb["image_index"]]) as limb_image:
                        with Image.open(self.output_folder_path + "/" + image_data[limb["image_index"]]["path"]) as limb_image:
                            adjusted_image = limb_image.copy()
                            # could probably make everything go down 1 tab since we don't need limb_image anymore?
                            rotate_type = None

                            if limb["flip_h"]:
                                adjusted_image = adjusted_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

                            # match limb["rotation"]:
                            match limb["rotation_amount"]:
                                case 1:
                                    rotate_type = Image.Transpose.ROTATE_90 if limb["flip_h"] else Image.Transpose.ROTATE_270
                                case 2:
                                    rotate_type = Image.Transpose.ROTATE_180
                                case 3:
                                    rotate_type = Image.Transpose.ROTATE_270 if limb["flip_h"] else Image.Transpose.ROTATE_90

                            if rotate_type:
                                adjusted_image = adjusted_image.transpose(rotate_type)

                            # x_offset_adjust, y_offset_adjust = x_offset + x_position, y_position + y_offset
                            
                            # layer_image.paste(adjusted_image, (x_offset_adjust, y_offset_adjust)) # this should PROBABLY be alpha composite to avoid cutoff issues
                            
                            
                            # stuff to prevent clipping with the different image sizes n stuff
                            adjusted_image_bbox = adjusted_image.getbbox()
                            if adjusted_image_bbox:
                                adjusted_image = adjusted_image.crop(adjusted_image_bbox)
                                # layer_image.paste(adjusted_image, (x_offset_adjust, y_offset_adjust))

                                # print(adjusted_image_bbox[0])
                                # print(adjusted_image_bbox[1])
                                # print(adjusted_image_bbox)
                                x_offset_adjust, y_offset_adjust = x_offset + x_position + adjusted_image_bbox[0], y_position + y_offset + adjusted_image_bbox[1]

                                layer_image.paste(adjusted_image, (x_offset_adjust, y_offset_adjust))
                                
                                
                                
                                # layer_image = Image.alpha_composite()

                                # return adjusted_image, x_offset_adjust, y_offset_adjust
        else:
            # this is assuming that there IS a search image. i dunno, i really oughta think of how to guarantee that and everything
            layer_image_path = ((self.output_folder_path + "/") if self.json_data["header"]["paths_are_local"] else "") + layer["search_image_path"]
            layer_image = Image.open(layer_image_path)

        return layer_image

    def export_layer(self):
        # layer_index = self.json_data["header"]["layer_names"]
        # layer_name = self.json_data["header"]["layer_names"][layer_index] # or, rather than using layername, could use string inside optionmenu?
        layer_name = self.layer_option.get() # or, rather than using layername, could use string inside optionmenu?

        # layer_index = self.json_data["header"]["layer_names"].index(layer_name) # will throw error if not a layer, soooo try/except?
        layer_data = self.json_data["layer_data"]
        layer_index = -1
        layer = None
        for i, l in enumerate(layer_data):
            if l["name"] == layer_name:
                layer_index = i
                layer = l
                break

        # layer_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")], initialfile= "export_" + self.json_data["header"]["name"] + "_" + layer_name + ".png")
        layer_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")], initialfile= "export_" + self.json_data["header"]["name"] + "_" + layer_name + ".png")
        
        # if border or cosmetic, make their respective image only. if not, 

        if layer_path:
            layer_image = self.format_layer(layer_index)

            # if (self.include_border.get()):
                # with Image.open(self.output_folder_path + "/" + self.json_data["header"]["border_image_path"]) as border_image:
                    # layer_image = Image.alpha_composite(layer_image, border_image)

            layer_image.save(layer_path)

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