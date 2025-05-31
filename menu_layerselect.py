import os
import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox, ttk
# from PIL import Image, ImageTk, ImageOps
from PIL import Image, ImageTk
from generate import GenerateJSON
from tooltip import ToolTip

from shared import on_global_click

import json

class Menu_LayerSelect(tk.Frame):
    def __init__(self, master, show_frame_callback):
        super().__init__(master)

        # self.root = root
        # self.root.title("Consistxels: Layer Selection")

        # in the future, should be taken from some style file
        self.bg_color = "#2e2e2e"
        self.fg_color = "#ffffff"
        self.secondary_bg = "#3a3a3a"
        self.secondary_fg = "#6a6a6a"
        self.button_bg = "#444"
        self.field_bg = "#222222"

        self.separator_style = ttk.Style().configure("Custom.TSeparator", background=self.secondary_fg)

        # Track images and border
        self.image_data = []  # List of dicts: {path, name, thumbnail, img_obj}
        self.border_image = None
        self.border_path = None
        self.border_color = "#00007f" # in the future, could be taken from info stored from last generation

        # self.root.configure(bg=self.bg_color)
        self.configure(bg=self.bg_color)

        self.setup_ui(show_frame_callback)

    def setup_ui(self, show_frame_callback):

        # Top frame for controls
        # self.top_frame = tk.Frame(self.root, bg=self.bg_color)
        self.top_frame = tk.Frame(self, bg=self.bg_color)
        self.top_frame.pack(fill="x", padx=10, pady=5)

        name_label = tk.Label(self.top_frame, text="Sprite sheet name:", bg=self.bg_color, fg=self.fg_color)
        name_label.pack(side="left", padx = 5, pady=5)
        
        self.name_entry_input = tk.StringVar()
        name_entry = tk.Entry(self.top_frame, width=32, bg=self.field_bg, fg=self.fg_color, textvariable=self.name_entry_input)
        name_entry.bind("<FocusIn>", self.on_entry_FocusIn)
        name_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        name_entry.pack(side="left", padx = 5)
        # name_entry.bind("<FocusOut>")

        ttk.Separator(self.top_frame, orient="vertical", style=self.separator_style).pack(fill="y", side="left", padx=5)

        add_images_button = tk.Button(self.top_frame, text="Add Images", command=self.add_images, bg=self.button_bg, fg=self.fg_color)
        add_images_button.pack(side="left", padx=5)
        ToolTip(add_images_button, "Add one more more images.")

        ttk.Separator(self.top_frame, orient="vertical", style=self.separator_style).pack(fill="y", side="left", padx=5)

        choose_border_button = tk.Button(self.top_frame, text="Choose Border", command=self.add_border, bg=self.button_bg, fg=self.fg_color)
        choose_border_button.pack(side="left", padx=5)
        ToolTip(choose_border_button, "Choose an image file containing the borders of the sprites' poses. This will be searched in order to find the poses and generate the data.")

        self.border_label = tk.Label(self.top_frame, text="No border selected", bg=self.bg_color, fg=self.fg_color)
        self.border_label.pack(side="left", padx=5)

        tk.Label(self.top_frame, text="Border Color:", bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=(20, 5))

        self.border_color_swatch = tk.Canvas(self.top_frame, width=20, height=20, bg=self.border_color,
        highlightthickness=1, highlightbackground="black")
        self.border_color_swatch.pack(side="left", padx=5)

        self.color_entry_input = tk.StringVar()
        self.color_entry_input.set(self.format_color_string(self.border_color))
        color_entry = tk.Entry(self.top_frame, width=10, bg=self.field_bg, fg=self.fg_color, textvariable=self.color_entry_input)
        color_entry.bind("<FocusIn>", self.on_entry_FocusIn)
        color_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        color_entry.bind("<FocusOut>", self.border_color_entry_input, add="+")
        color_entry.pack(side="left", padx = 5)
        ToolTip(color_entry, "Type the color that will be interpreted as the border.")

        pick_border_color_button = tk.Button(self.top_frame, text="Open Color Picker", command=self.pick_color, bg=self.button_bg, fg=self.fg_color)
        pick_border_color_button.pack(side="left", padx=5)
        ToolTip(pick_border_color_button, "Pick the color that will be interpreted as the border.")

        ttk.Separator(self.top_frame, orient="vertical", style=self.separator_style).pack(fill="y", side="left", padx=5)

        back_button = tk.Button(self.top_frame, text="Back to Main Menu", bg=self.button_bg, fg=self.fg_color, command=lambda: show_frame_callback("Main"))
        back_button.pack(side="right", padx=5)
        ToolTip(back_button, "...Come on, this one is self explanatory.", False, True, 2000)

        # Main frame split left/right
        # self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame = tk.Frame(self, bg=self.bg_color)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        # Left scrollable frame for image entries
        self.left_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.left_frame.pack(side="left", fill="y", padx=(5, 10))

        self.canvas = tk.Canvas(self.left_frame, width=400, bg=self.bg_color, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.left_frame, orient="vertical", command=self.canvas.yview)
        # self.scrollbar.configure(bg=self.secondary_bg, fg=self.secondary_fg)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg_color)

        self.scrollable_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="y")
        self.scrollbar.pack(side="right", fill="y")

        # Mousewheel scrolling
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        # Right canvas for preview
        self.preview_canvas = tk.Canvas(self.main_frame, width=400, height=400, bg=self.field_bg)
        # self.preview_canvas.bind("<Configure>", self.update_preview)

        self.preview_canvas.pack(side="left", fill="both", expand=True)
        # ToolTip(self.preview_canvas, '''A preview image of all the layers you've added, in order.''')

        # Footer frame
        # self.footer = tk.Frame(self.root, bg=self.bg_color)
        self.footer = tk.Frame(self, bg=self.bg_color)
        self.footer.pack(fill="x", padx=10, pady=5)
        self.footer.pack_propagate(True)

        self.update_preview_button = tk.Button(self.footer, text="Update Preview", command=self.update_preview, bg=self.button_bg, fg=self.fg_color)
        self.update_preview_button.pack(side="left", padx=5, pady=5)
        ToolTip(self.update_preview_button, "Update the preview image that contains all layers ordered as shown. (May take a while if you have a lot of images)\n\nIf the button is yellow, changes have been made, and the preview can be updated.", True)
        
        ttk.Separator(self.footer, orient="vertical", style=self.separator_style).pack(fill="y", side="left", padx=5)

        self.start_search_in_center = tk.BooleanVar()
        start_search_in_center_checkbutton = tk.Checkbutton(self.footer, text="Start search in center", bg=self.bg_color, fg=self.fg_color, selectcolor=self.button_bg, onvalue=True, offvalue=False, variable=self.start_search_in_center)
        start_search_in_center_checkbutton.pack(side="left", padx=5, pady=5)
        start_search_in_center_checkbutton.select()
        ToolTip(start_search_in_center_checkbutton, "When searching the spritesheet, the program will look at each row starting in the middle of the image, rather than at the edge.\nIt will search outward in one direction before reaching the edge, at which point it will search in the other direction, before moving onto the next row.\nRecommended for sprite sheets that group poses in a vertical formation, as it makes the order that pose images are found in much more intuitive. Not recommended if \"Search right-to-left\" is enabled.", True)
        
        self.search_right_to_left = tk.BooleanVar()
        search_right_to_left_checkbutton = tk.Checkbutton(self.footer, text="Search right-to-left", bg=self.bg_color, fg=self.fg_color, selectcolor=self.button_bg, onvalue=True, offvalue=False, variable=self.search_right_to_left)
        search_right_to_left_checkbutton.pack(side="left", padx=5, pady=5)
        ToolTip(search_right_to_left_checkbutton, "Search the spritesheet from right-to-left, instead of from left-to-right.\nRecommended if \"Start search in center\" is disabled, as most characters face right by default,\nand most sprite sheets show the rightmost sprites on the right side of the sheet, so the generated data will use the right-facing poses as the defaults.", True)

        ttk.Separator(self.footer, orient="vertical", style=self.separator_style).pack(fill="y", side="left", padx=5)
        # tk.Button(self.footer, text="Zoom In", command=lambda: self.change_zoom(1.1)).pack(side="right", padx=5)
        # tk.Button(self.footer, text="Zoom Out", command=lambda: self.change_zoom(0.9)).pack(side="right")

        self.padding_types = ["Show only always-visible pixels", "Show all theoretically-visible pixels", "None"]

        padding_label = tk.Label(self.footer, text="Automatic padding type:", bg=self.bg_color, fg=self.fg_color)
        padding_label.pack(side="left", padx=5, pady=5)
        ToolTip(padding_label, "- Show only always-visible pixels: Padding for pose images will increase to show how much space is visible in all instances of that pose image. (Recommended)\n- Show all theoretically-visible pixels: Same as above, but padding also contains space that is not visible in some pose boxes.\n- None: No extra automatic padding is applied. Recommended if using the \"Custom padding\" option.", True)

        self.padding_type_option = tk.StringVar(value=self.padding_types[0])
        # self.padding_type_option.set("Show only always-visible pixels")

        padding_type_optionmenu = tk.OptionMenu(self.footer, self.padding_type_option, *self.padding_types)
        padding_type_optionmenu.configure(bg=self.bg_color, fg=self.fg_color, activebackground=self.secondary_bg, activeforeground=self.fg_color, width=28, anchor="w", justify="left")
        padding_type_optionmenu["menu"].configure(bg=self.field_bg, fg=self.fg_color, activebackground=self.secondary_bg, activeforeground=self.fg_color)
        padding_type_optionmenu.pack(side="left", padx=5, pady=5)
        ToolTip(padding_type_optionmenu, "- Show only always-visible pixels: Padding for pose images will increase to show how much space is visible in all instances of that pose image. (Recommended)\n- Show all theoretically-visible pixels: Same as above, but padding also contains space that is not visible in some pose boxes.\n- None: No extra automatic padding is applied. Recommended if using the \"Custom padding\" option.", True)

        # custom_padding_label = tk.Label(self.footer, text="Custom padding amount:", bg=self.bg_color, fg=self.fg_color)
        # custom_padding_label.pack(side="left", padx=5, pady=5)

        tk.Label(self.footer, text="Custom padding amount:", bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=5, pady=5)

        self.custom_padding = tk.IntVar()
        self.custom_padding.set(0)

        custom_padding_entry = tk.Entry(self.footer, bg=self.field_bg, fg=self.fg_color, textvariable=self.custom_padding, width=8) # string values will mess everything up!
        custom_padding_entry.pack(side="left", padx=5, pady=5)
        custom_padding_entry.bind("<FocusIn>", self.on_entry_FocusIn)
        custom_padding_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        ToolTip(custom_padding_entry, "Enter a custom amount of padding to apply to each pose image. If used alongside automatic padding, this will add the automatic and custom padding together.\n(Negative values are allowed, and will instead subtract from automatic padding without cutting off any of the pose images.)", True)

        ttk.Separator(self.footer, orient="vertical", style=self.separator_style).pack(fill="y", side="left", padx=5)

        self.generate_button = tk.Button(self.footer, text="Generate...", command=self.generate_output, bg=self.button_bg, fg=self.fg_color)
        self.generate_button.pack(side="right", padx=5, pady=5)
        ToolTip(self.generate_button, "Generate data! (May take a while)", True, True)

        ttk.Separator(self.footer, orient="vertical", style=self.separator_style).pack(fill="y", side="right", padx=5)
        
        export_layer_select_json_button = tk.Button(self.footer, bg=self.button_bg, fg=self.fg_color, text="Export...", command=self.export_layer_select_json)
        export_layer_select_json_button.pack(side="right", padx=5, pady=5)
        ToolTip(export_layer_select_json_button, "Export a .json file containing the layer information, so you don't have to fill out the layer info again.", True, True) # explain better. also, it IS possible to use an output .json, you just gotta be smart about it.

        import_layer_select_json_button = tk.Button(self.footer, bg=self.button_bg, fg=self.fg_color, text="Import...", command=self.import_layer_select_json)
        import_layer_select_json_button.pack(side="right", padx=5, pady=5)
        ToolTip(import_layer_select_json_button, "Import a .json file containing the layer information.\n(DO NOT use a .json generated with the \"Generate...\" button!)", True, True) # explain better. also, it IS possible to use an output .json, you just gotta be smart about it.



        self.bind_all("<Button-1>", on_global_click, add="+")

    def on_mousewheel(self, event):
        delta = -1 * (event.delta // 120)
        self.canvas.yview_scroll(delta, "units")

    def on_entry_FocusIn(self, event):
        event.widget.configure(bg=self.secondary_bg)
    
    def on_entry_FocusOut(self, event):
        event.widget.configure(bg=self.field_bg)

    def pick_color(self):
        color = colorchooser.askcolor(title="Pick Background Color")[1]
        if color:
            # self.color_entry.delete(0, tk.END)
            # self.color_entry.insert(0, color)

            # self.border_color_

            # self.update_colors(color)
            self.update_border_color(color)

    def update_border_color(self, color = None):
        # if color == "<FocusOut event>":
        #     color = self.color_entry_input.get()
        #     # print(color)
        #     # check that string input is valid. else, return. ...or maybe just try/except below?
        # else:
        #     self.color_entry_input.set(color)
        
        # strip # from left
        # add # to left

        try:
            color = self.format_color_string(color)
            # print(color)

            self.border_color_swatch.configure(bg=color)
            self.color_entry_input.set(color)
            self.border_color = color
        except:
            messagebox.showerror("Error", "Enter a valid color")

    def border_color_entry_input(self, _event):
        self.update_border_color(self.color_entry_input.get())
    
    def format_color_string(self, color):
        # color = ""
        # print("gothere1")
        color = color.lstrip("#")
        # print("gothere2")
        color = "#" + color
        # print("gothere3")
        return color

    def add_images(self, data = None):
        # paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])


        if not data:
            paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])

            # data["path"] = 
            # data["name"] =
            data = []
            for path in paths:
                data.append({"path": path, "name": os.path.splitext(os.path.basename(path))[0], "alt_source": None})
        # else:
        #     paths = []
        #     for d in data:
        #         # paths.append(d["path"])
        #         pass
        
        # for i, path in enumerate(paths):
        for d in data:



            # filename = os.path.basename(path)
            # name = os.path.splitext(filename)[0]
            
            path = d["path"]
            name = d["name"]
            alt_source = d["alt_source"]

            image = Image.open(path)

            if len(self.image_data):
                if self.image_data[0]["img"].size != image.size:
                    image.close()
                    messagebox.showwarning("Warning", "All images must be the same size")
                    break
            if self.border_image != None:
                if self.border_image.size != image.size:
                    image.close()
                    messagebox.showwarning("Warning", "All images must be the same size as the border")
                    break

            thumb = image.copy()
            thumb.thumbnail((64, 64))
            photo = ImageTk.PhotoImage(thumb)
            self.image_data.append({"path": path, "name": name, "img": image, "thumb": photo, "alt_source": alt_source})
        
        self.redraw_image_entries()
        # self.update_preview()
        self.update_preview_button.configure(bg="#ffff00", fg="#000000")

    def add_border(self, path = None):
        if path == None:
            path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])

        if path:
            if self.border_image != None:
                self.border_image.close()

            temp_border_image = Image.open(path)

            if len(self.image_data):
                if self.image_data[0]["img"].size != temp_border_image.size:
                    temp_border_image.close()
                    messagebox.showwarning("Warning", "The border must be the same size as the images")
                    return
            
            self.border_image = temp_border_image

            self.border_path = path
            self.border_label.config(text=os.path.basename(path))
            # self.update_preview()
            self.update_preview_button.configure(bg="#ffff00", fg="#000000")

    def move_image(self, index, direction):
        new_index = index + direction
        if 0 <= new_index < len(self.image_data):
            self.image_data[index], self.image_data[new_index] = self.image_data[new_index], self.image_data[index]
            self.redraw_image_entries()
            # self.update_preview()
            self.update_preview_button.configure(bg="#ffff00", fg="#000000")

    def delete_image(self, index):
        # close image
        self.image_data[index]["img"].close()

        del self.image_data[index]
        self.redraw_image_entries()
        # self.update_preview()
        self.update_preview_button.configure(bg="#ffff00", fg="#000000")

    def redraw_image_entries(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for i, data in enumerate(self.image_data):
            frame = tk.Frame(
                self.scrollable_frame,
                bg=self.secondary_bg,
                relief=tk.RIDGE,
                bd=2,
                padx=5,
                pady=5
            )

            frame.pack(fill="x", anchor="w", pady=2, padx=(10, 0))
            # frame.pack_propagate(True)

            tk.Label(frame, text=f"Layer {i+1}", bg=self.secondary_bg, fg=self.fg_color).grid(row=0, column=1, sticky="w")

            img_label = tk.Label(frame, image=data["thumb"], bg=self.secondary_bg)
            img_label.grid(row=0, column=0, rowspan=2, padx=5)

            tk.Label(frame, text="Name:", bg=self.secondary_bg, fg=self.fg_color).grid(row=1, column=1, sticky="e")
            name_entry = tk.Entry(frame, width=15, bg=self.field_bg, fg=self.fg_color)
            name_entry.bind("<FocusIn>", self.on_entry_FocusIn, add="+")
            name_entry.bind("<FocusOut>", self.on_entry_FocusOut, add="+")
            name_entry.insert(0, data["name"])
            name_entry.grid(row=1, column=2, sticky="w")

            def save_name(e, entry=data, entry_widget=name_entry):
                entry["name"] = entry_widget.get()

            name_entry.bind("<FocusOut>", save_name, add="+")

            alt_source_button = tk.Button(frame, text="@", bg=self.button_bg, fg=("#00f870" if data["alt_source"] else self.fg_color))
            # alt_source_button.grid(row=0, column=3, rowspan=2, padx=5)
            alt_source_button.grid(row=0, column=3, padx=5)
            alt_source_button.configure(command=lambda idx=i, widget=alt_source_button: self.add_alternate_image_source(idx, widget))
            ToolTip(alt_source_button, "Add an alternate image that will be used as the source for exported pose images.\n\nThe main image is the one being searched, and by default, the source for\npose images as well. Adding an alternate image makes it so replacing one large sheet's poses with\nanother's is easier, and you don't have to manually copy-paste everything.\n\n(Just leave this alone if you're not sure.)")

            x_button = tk.Button(frame, text="X", fg="red", command=lambda idx=i: self.delete_image(idx), bg=self.button_bg)
            # x_button.grid(row=0, column=3, rowspan=2, padx=5)
            x_button.grid(row=1, column=3, padx=5)
            ToolTip(x_button, f"Delete layer {i+1}")

            up_button = tk.Button(frame, text="↑", command=lambda idx=i: self.move_image(idx, -1), bg=self.button_bg, fg=self.fg_color)
            up_button.grid(row=0, column=4)
            ToolTip(up_button, f"Reorder layer {i+1} upwards")

            down_button = tk.Button(frame, text="↓", command=lambda idx=i: self.move_image(idx, 1), bg=self.button_bg, fg=self.fg_color)
            down_button.grid(row=1, column=4, padx=5)
            ToolTip(down_button, f"Reorder layer {i+1} downwards")

            self.scrollable_frame.bind_all("<Button-1>", on_global_click, add="+")

    def add_alternate_image_source(self, index, widget):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if path:
            self.image_data[index]["alt_source"] = path
            widget.configure(fg="#00f870")

    def update_preview(self):
        self.update_preview_button.configure(bg=self.button_bg, fg=self.fg_color)

        width = self.preview_canvas.winfo_width()
        height = self.preview_canvas.winfo_height()
        composite = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        def paste_center(base, img):
            img_ratio = min(width / img.width, height / img.height)
            new_size = (int(img.width * img_ratio), int(img.height * img_ratio))
            
            # zoomed_size = (int(img.width * self.zoom_level), int(img.height * self.zoom_level))
            # resized = img.resize(zoomed_size, Image.Resampling.LANCZOS)

            resized = img.resize(new_size, Image.Resampling.LANCZOS)

            offset = ((width - new_size[0]) // 2, (height - new_size[1]) // 2)
            base.paste(resized, offset, resized if resized.mode == 'RGBA' else None)

        if self.border_image:
            paste_center(composite, self.border_image)
        for item in reversed(self.image_data):
            paste_center(composite, item["img"])

        self.preview_image = ImageTk.PhotoImage(composite)
        self.preview_canvas.delete("all")
        self.preview_canvas.create_image(width // 2, height // 2, image=self.preview_image)

    # def change_zoom(self, factor):
    #     self.zoom_level *= factor
    #     self.update_preview()

    def export_layer_select_json(self):
        name = self.name_entry_input.get()
        if not name:
            name = "unnamed_sprite_sheet"

        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Json File", "*.json")], initialfile="consistxels_" + name + "_layers.json")
        if path:

            header = {
                # "name": self.name_entry_input.get(),
                "name": name,
                "border_color": self.border_color,
                "border_path": self.border_path,
                "start_search_in_center": self.start_search_in_center.get(),
                "search_right_to_left": self.search_right_to_left.get(),
                "automatic_padding_type": self.padding_types.index(self.padding_type_option.get()),
                "custom_padding_amount": self.custom_padding.get()
            }

            layer_data = []

            for image in self.image_data:
                layer_data.append({"path": image["path"], "name": image["name"], "alt_source": image["alt_source"]})

            export = {"header": header, "layer_data": layer_data}

            with open(path, 'w') as file:
                json.dump(export, file, indent=4)

    def import_layer_select_json(self):
        path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("Json File", "*.json")])
        if path:
            with open(path) as json_file:
                json_data = json.load(json_file)
                header = json_data["header"]
                layer_data = json_data["layer_data"]

                self.name_entry_input.set(header["name"])

                self.update_border_color(self.format_color_string(header["border_color"]))

                self.add_border(header["border_path"])

                # if header["start_search_in_center"]:
                self.start_search_in_center.set(header["start_search_in_center"])

                self.search_right_to_left.set(header["search_right_to_left"])
                # if header["search_right_to_left"]:
                    # pass

                self.padding_type_option.set(self.padding_types[header["automatic_padding_type"]])

                self.custom_padding.set(header["custom_padding_amount"])

                # delete current images too!!!
                self.add_images(layer_data)


            

    def generate_output(self):
        # border image
        # border color
        # image info list:
        # - image
        # - name

        image_info = []
        duplicate_layer_name = False
        for data in self.image_data:
            if data["name"] in [image["name"] for image in image_info]:
                duplicate_layer_name = True
                break
            image_info.append({"path": data["path"], "name": data["name"], "alt_source": data["alt_source"]})
        # print(image_info)
        
        # print(self.search_right_to_left.get())

        # get some variables
        name = self.name_entry_input.get()
        
        # TODO: check that border and all images are the same size.
        # could just check images when uploading - they all need to be the same size, etc.
        # that way we could just check against ONE of the images! which is doable I think
        if self.border_path != None and len(image_info) > 0 and name != "" and not duplicate_layer_name:
            if self.border_color == None: self.border_color = "#000000"

            # TODO: close images when moving to other menu!!!
            # in fact, have a function that specifically closes the images and moves onto next menu

            # raises error if not one of the types
            padding_type = self.padding_types.index(self.padding_type_option.get())

            GenerateJSON(name, self.border_path, self.border_color, image_info, self.start_search_in_center.get(), self.search_right_to_left.get(), padding_type, self.custom_padding.get())
            # NEED to do some sort of awaiting, then some sort of "Complete!" messagebox
        else:
            warning_output = ""

            if self.border_path == None: warning_output += "Please add a border image"
            if len(image_info) <= 0:
                if warning_output != "": warning_output += "\n"
                warning_output += "Please add at least one layer image"
            if name == "":
                if warning_output != "": warning_output += "\n"
                warning_output += "Please enter a name for this sprite sheet"
            if duplicate_layer_name:
                if warning_output != "": warning_output += "\n"
                warning_output += "Ensure all layers have unique names"

            messagebox.showwarning("Wait!", warning_output)