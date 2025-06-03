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

        # in the future, should be taken from some style file
        self.bg_color = "#2e2e2e"
        self.fg_color = "#ffffff"
        self.secondary_bg = "#3a3a3a"
        self.secondary_fg = "#6a6a6a"
        self.button_bg = "#444"
        self.field_bg = "#222222"

        # Track images and border
        self.image_data = []  # List of dicts: {path, name, thumbnail, img_obj}
        self.border_image = None
        self.border_path = None
        self.border_color = "#00007f" # in the future, could be taken from info stored from last generation

        # self.root.configure(bg=self.bg_color)
        self.configure(bg=self.bg_color)

        self.setup_ui(show_frame_callback)

    def setup_ui(self, show_frame_callback):

        # Header
        self.header = tk.Frame(self, bg=self.bg_color)
        self.header.pack(fill="x", padx=2)

        # Header left:

        # Save button
        save_json_button = tk.Button(self.header, text="💾 Save .json", bg=self.button_bg, fg=self.fg_color, command=self.export_layer_select_json)
        save_json_button.pack(padx=10, pady=10, side="left")
        ToolTip(save_json_button, "Save the selected search options and layer data to a .json file for later use.\nShould ONLY be used locally, and not transferred to other devices, as this uses\ndirect paths to layer images that are specific to this device.")

        # Save folder button (NOT sure if i CAN save to a .zip.)
        save_folder_button = tk.Button(self.header, text="💾 Save all to folder", bg=self.button_bg, fg=self.fg_color, command=self.export_layer_select_json)
        save_folder_button.pack(padx=(0,10), pady=10, side="left")
        ToolTip(save_folder_button, "Save the selected search options, layer data, and layer images to a specified folder.\nThis avoids the problem with the 'Save .json' option, and the folder can be\ntransferred to other devices without issue.\n(It's recommended that you choose a new, EMPTY folder, so as to not clutter up your files!)")
        
        # Load button
        load_button = tk.Button(self.header, text="📁 Load", bg=self.button_bg, fg=self.fg_color, command=self.import_layer_select_json)
        load_button.pack(padx=(0,10), pady=10, side="left")
        ToolTip(load_button, "Load a .json file and restore previous search options and layer data.\n(Works with both of the previous 'Save' options, as well as generated pose data output.)")

        # New button
        new_button = tk.Button(self.header, text="➕ New", bg=self.button_bg, fg=self.fg_color)
        new_button.pack(padx=(0,10), pady=10, side="left")
        ToolTip(new_button, "Reset all options, delete all layers, and start from scratch.")

        # Header right:

        # Back button
        back_button = tk.Button(self.header, text="Back to Main Menu", bg=self.button_bg, fg=self.fg_color, command=lambda: show_frame_callback("Main"))
        back_button.pack(side="right", padx=10, pady=10)
        ToolTip(back_button, "...Come on, this one is self explanatory.", False, True, 2000)

        # Main frame
        self.main_frame = tk.Frame(self, bg=self.bg_color)
        self.main_frame.pack(fill="both", expand=True)

        paned_window = tk.PanedWindow(self.main_frame, bg=self.bg_color, opaqueresize=False, sashrelief="flat", sashwidth=16, bd=0)
        paned_window.pack(fill="both", expand=True)

        # Left frame
        self.left_frame = tk.Frame(paned_window, bg=self.bg_color, width=480, highlightthickness=1, highlightbackground=self.secondary_fg)
        self.left_frame.pack(side="left", fill="y", padx=10)
        self.left_frame.pack_propagate(False)

        # Center frame
        self.center_frame = tk.Frame(paned_window, bg=self.field_bg, highlightthickness=1, highlightbackground=self.secondary_fg)
        self.center_frame.pack(side="right", fill="both", padx=10, expand=True)

        # Right frame
        self.right_frame = tk.Frame(paned_window, bg=self.bg_color, width=600, highlightthickness=1, highlightbackground=self.secondary_fg)
        self.right_frame.pack(side="right", fill="y", padx=10)
        self.right_frame.pack_propagate(False)

        paned_window.add(self.left_frame, minsize=360, stretch="never")
        paned_window.add(self.center_frame, minsize=0, stretch="always")
        paned_window.add(self.right_frame, minsize=400, stretch="never")
        
        # Layer options:

        # Layer header
        layer_header = tk.Frame(self.left_frame, bg=self.bg_color, highlightthickness=1, highlightbackground=self.secondary_fg)
        layer_header.pack(side="top", fill="x")

        # Layer main frame
        layer_main_frame = tk.Frame(self.left_frame, bg=self.bg_color, highlightthickness=1, highlightbackground=self.secondary_fg)
        layer_main_frame.pack(side="top", fill="both", expand=True)

        # Actual layer menu
        self.layer_canvas = tk.Canvas(layer_main_frame, bg=self.bg_color, width=0, highlightthickness=1, highlightbackground=self.secondary_fg)
        self.layer_scrollbar = tk.Scrollbar(layer_main_frame, orient="vertical", command=self.layer_canvas.yview)
        self.scrollable_frame = tk.Frame(self.layer_canvas, bg=self.bg_color)

        # Bind scrolling
        self.scrollable_frame.bind(
            "<Configure>", lambda e: self.layer_canvas.configure(scrollregion=self.layer_canvas.bbox("all"))
        )

        # Create canvas in which to show layer info
        self.layer_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.layer_canvas.configure(yscrollcommand=self.layer_scrollbar.set)

        self.layer_canvas.pack(side="left", fill="both", expand=True)
        self.layer_scrollbar.pack(side="left", fill="y")

        # Mousewheel scrolling
        self.layer_canvas.bind_all("<MouseWheel>", self.on_mousewheel) # don't do bind ALL, just stuff inside layer_canvas, or maybe inside left_frame

        # Layer footer
        layer_footer = tk.Frame(self.left_frame, bg=self.bg_color, highlightthickness=1, highlightbackground=self.secondary_fg)
        layer_footer.pack(side="top", fill="x")

        # Top add buttons
        layer_add_blank_top = tk.Button(layer_header, text="➕ Blank layer", bg=self.button_bg, fg=self.fg_color)
        layer_add_blank_top.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        ToolTip(layer_add_blank_top, "Add a blank layer as the top layer.")

        layer_add_images_top = tk.Button(layer_header, text="➕ From image(s)", bg=self.button_bg, fg=self.fg_color, command=self.add_images)
        layer_add_images_top.pack(side="right", padx=(0,10), pady=10, fill="x", expand=True)
        ToolTip(layer_add_images_top, "Add image(s) as the top layer(s). Layer's name will be autofilled with its image's filename.")

        # Bottom add buttons (NEED SOME WAY TO MAKE IT ADD TO BOTTOM/TOP CORRECTLY)
        layer_add_blank_bottom = tk.Button(layer_footer, text="➕ Blank layer", bg=self.button_bg, fg=self.fg_color)
        layer_add_blank_bottom.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        ToolTip(layer_add_blank_bottom, "Add a blank layer as the bottom layer.", True)

        layer_add_images_bottom = tk.Button(layer_footer, text="➕ From image(s)", bg=self.button_bg, fg=self.fg_color, command=self.add_images)
        layer_add_images_bottom.pack(side="right", padx=(0,10), pady=10, fill="x", expand=True)
        ToolTip(layer_add_images_bottom, "Add image(s) as the bottom layer(s). Layer's name will be autofilled with its image's filename.", True)

        # Center preview:

        # Preview canvas
        self.preview_canvas = tk.Canvas(self.center_frame, bg=self.field_bg, highlightthickness=1, highlightbackground=self.secondary_fg)
        self.preview_canvas.pack(side="top", fill="both", expand=True)

        # Canvas scroll bars
        preview_canvas_vert_scroll = tk.Scrollbar(self.preview_canvas, orient="vertical", command=self.preview_canvas.yview)
        preview_canvas_vert_scroll.pack(side="right", fill="y", padx=1, pady=1)

        preview_canvas_hori_scroll = tk.Scrollbar(self.preview_canvas, orient="horizontal", command=self.preview_canvas.xview)
        preview_canvas_hori_scroll.pack(side="bottom", fill="x", padx=1, pady=1)

        # Canvas buttons have to go *some*where.
        # (would really like this to be ON the canvas at some point.)
        canvas_buttons_frame = tk.Frame(self.center_frame, bg=self.bg_color, highlightthickness=1, highlightbackground=self.secondary_fg)
        canvas_buttons_frame.pack(side="top", fill="x")

        # Bottomleft reload button
        self.update_preview_button = tk.Button(canvas_buttons_frame, text="Update Preview", command=self.update_preview, bg=self.button_bg, fg=self.fg_color)
        self.update_preview_button.pack(side="left", padx=10, pady=10) # figure out how to get bottom-left
        ToolTip(self.update_preview_button, "Update the preview image that contains all layers ordered as shown. (May take a while if you have a lot of images)\n\nIf the button is yellow, changes have been made, and the preview can be updated.", True)

        # Bottomright zoom buttons
        zoom_in_button = tk.Button(canvas_buttons_frame, text="➕", bg=self.button_bg, fg=self.fg_color)
        zoom_in_button.pack(side="right", padx=(5, 10), pady=10)
        ToolTip(zoom_in_button, "Zoom in", True)

        zoom_out_button = tk.Button(canvas_buttons_frame, text="➖", bg=self.button_bg, fg=self.fg_color)
        zoom_out_button.pack(side="right", padx=(10, 5), pady=10)
        ToolTip(zoom_out_button, "Zoom out", True)

        # Right menu:

        # I want to find a way to make this more prominent somehow. It's VERY important and shouldn't be missed.
        name_frame = tk.Frame(self.right_frame, bg=self.bg_color, highlightthickness=1, highlightbackground=self.secondary_fg)
        name_frame.pack(side="top", fill="x")

        name_label = tk.Label(name_frame, text="Sprite sheet name:", bg=self.bg_color, fg=self.fg_color)
        name_label.pack(side="left", padx=10, pady=10)

        self.name_entry_input = tk.StringVar()
        name_entry = tk.Entry(name_frame, bg=self.field_bg, fg=self.fg_color, textvariable=self.name_entry_input)
        name_entry.bind("<FocusIn>", self.on_entry_FocusIn) # this is NOT for saving name info - it's for focusing/unfocusing textbox on global click (i think)
        name_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        name_entry.pack(side="left", fill="x", expand=True, padx=(0,10), pady=10)
        ToolTip(name_entry, "Enter the name of the sprite sheet, which is used to display and organize some information.") # make better desc

        # Search type

        self.search_types = ["Border", "Spacing", "Preset"]

        search_type_frame = tk.Frame(self.right_frame, bg=self.bg_color, highlightthickness=1, highlightbackground=self.secondary_fg, height=240)
        search_type_frame.pack(side="top", fill="x")
        search_type_frame.pack_propagate(False)

        search_type_option_frame = tk.Frame(search_type_frame, bg=self.bg_color)
        search_type_option_frame.pack(side="top", fill="x")

        search_type_label = tk.Label(search_type_option_frame, text="Search type:", bg=self.bg_color, fg=self.fg_color)
        search_type_label.pack(side="left", padx=10, pady=10)
        ToolTip(search_type_label, "- Border: Searches a border image for boxes that contain poses. When selected, a border\nlayer will be automatically created. Add a valid image, with *perfectly rectangular* pose boxes.\n\n- Spacing: Poses are assumed to be spaced out equally from each other.\n\n- Preset: Use a valid .json file that contains pose data (i.e., one generated with the\n\"Generate Pose Data...\" button) to search for poses in already-known locations.", False, True)

        self.search_type_option = tk.StringVar(value=self.search_types[0])

        search_type_subframe_container_frame = tk.Frame(search_type_frame, bg=self.bg_color)
        search_type_subframe_container_frame.pack(side="top", fill="both", expand=True)

        search_border_subframe = tk.Frame(search_type_subframe_container_frame, bg=self.bg_color)
        search_border_subframe.place(relx=0, rely=0, relwidth=1, relheight=1)

        search_spacing_subframe = tk.Frame(search_type_subframe_container_frame, bg=self.bg_color)
        search_spacing_subframe.place(relx=0, rely=0, relwidth=1, relheight=1)

        search_preset_subframe = tk.Frame(search_type_subframe_container_frame, bg=self.bg_color)
        search_preset_subframe.place(relx=0, rely=0, relwidth=1, relheight=1)

        search_type_subframes = [search_border_subframe, search_spacing_subframe, search_preset_subframe]

        def search_type_option_selected(selected_option):
            search_type_subframes[self.search_types.index(selected_option)].lift()

            # TODO: other stuff for creating border image, etc.

        search_type_option_selected("Border")

        search_type_optionmenu = tk.OptionMenu(search_type_option_frame, self.search_type_option, *self.search_types, command=search_type_option_selected)
        # something to make the border stuff show up in the layers section (see above, i think)
        search_type_optionmenu.configure(bg=self.field_bg, fg=self.fg_color, activebackground=self.bg_color, activeforeground=self.fg_color, anchor="w", justify="left", highlightthickness=1, highlightbackground=self.secondary_fg, bd=0, relief="flat")
        search_type_optionmenu["menu"].configure(bg=self.field_bg, fg=self.fg_color, activebackground=self.secondary_bg, activeforeground=self.fg_color)
        search_type_optionmenu.pack(side="left", padx=(0,10), pady=10, fill="x", expand=True)
        ToolTip(search_type_optionmenu, "- Border: Searches a border image for boxes that contain poses. When selected, a border\nlayer will be automatically created. Add a valid image, with *perfectly rectangular* pose boxes.\n\n- Spacing: Poses are assumed to be spaced out equally from each other.\n\n- Preset: Use a valid .json file that contains pose data (i.e., one generated with the\n\"Generate Pose Data...\" button) to search for poses in already-known locations.", False, True)

        # Border subframe

        choose_border_button = tk.Button(search_border_subframe, text="Choose Border", command=self.add_border, bg=self.button_bg, fg=self.fg_color)
        choose_border_button.grid(padx=10, pady=10, row=0, column=1)
        ToolTip(choose_border_button, "Choose an image file containing the borders of the sprites' poses. This will be searched in order to find the poses and generate the data.")

        self.border_label = tk.Label(search_border_subframe, text="No border selected", bg=self.bg_color, fg=self.fg_color)
        self.border_label.grid(padx=0, pady=10, row=0, column=2)

        tk.Label(search_border_subframe, text="Border Color:", bg=self.bg_color, fg=self.fg_color).grid(padx=5, pady=5, row=1, column=1)

        border_color_swatch_and_entry_frame = tk.Frame(search_border_subframe, bg=self.bg_color)
        border_color_swatch_and_entry_frame.grid(row=1, column=2)

        self.border_color_swatch = tk.Canvas(border_color_swatch_and_entry_frame, width=20, height=20, bg=self.border_color,
        highlightthickness=1, highlightbackground="black")
        self.border_color_swatch.pack(side="left", padx=5, pady=5)

        self.color_entry_input = tk.StringVar()
        self.color_entry_input.set(self.format_color_string(self.border_color))
        
        color_entry = tk.Entry(border_color_swatch_and_entry_frame, width=10, bg=self.field_bg, fg=self.fg_color, textvariable=self.color_entry_input)
        color_entry.bind("<FocusIn>", self.on_entry_FocusIn)
        color_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        color_entry.bind("<FocusOut>", self.border_color_entry_input, add="+")
        color_entry.pack(side="left", padx=5, pady=5)
        ToolTip(color_entry, "Type the color that will be interpreted as the border.")

        pick_border_color_button = tk.Button(search_border_subframe, text="Open Color Picker", command=self.pick_color, bg=self.button_bg, fg=self.fg_color)
        pick_border_color_button.grid(padx=5, pady=5, row=1, column=3)
        ToolTip(pick_border_color_button, "Open a color picker and pick the color that will be interpreted as the border.") # would be better if it relied on detected border color!

        # Spacing subframe

        # Outer padding
        outer_padding_frame = tk.Frame(search_spacing_subframe, bg=self.bg_color)
        outer_padding_frame.pack(side="top", fill="x")

        tk.Label(outer_padding_frame, bg=self.bg_color, fg=self.fg_color, text="Outer padding:").pack(side="left", padx=(10,5), pady=10)

        self.outer_padding = tk.StringVar()
        self.outer_padding.set("0")
        outer_padding_entry = tk.Entry(outer_padding_frame, bg=self.field_bg, fg=self.fg_color, width=12, textvariable=self.outer_padding)
        outer_padding_entry.pack(side="left")
        outer_padding_entry.bind("<FocusIn>", self.on_entry_FocusIn)
        outer_padding_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        ToolTip(outer_padding_entry, "How much space between the sprites and the edge of the sprite sheet?", False, True)

        tk.Label(outer_padding_frame, bg=self.bg_color, fg=self.fg_color, text="px").pack(side="left", padx=(5,10), pady=10)

        # Inner padding
        inner_padding_frame = tk.Frame(search_spacing_subframe, bg=self.bg_color)
        inner_padding_frame.pack(side="top", fill="x")

        tk.Label(inner_padding_frame, bg=self.bg_color, fg=self.fg_color, text="Inner padding:").pack(side="left", padx=(10,5), pady=10)

        self.inner_padding = tk.StringVar()
        self.inner_padding.set("0")
        inner_padding_entry = tk.Entry(inner_padding_frame, bg=self.field_bg, fg=self.fg_color, width=12, textvariable=self.inner_padding)
        inner_padding_entry.pack(side="left", pady=10)
        inner_padding_entry.bind("<FocusIn>", self.on_entry_FocusIn)
        inner_padding_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        ToolTip(inner_padding_entry, "How much extra padding around each sprite?", False, True)

        inner_px_label = tk.Label(inner_padding_frame, bg=self.bg_color, fg=self.fg_color, text="px")
        inner_px_label.pack(side="left", padx=(5,10), pady=10)

        # Spacing
        spacing_frame = tk.Frame(search_spacing_subframe, bg=self.bg_color)
        spacing_frame.pack(side="top", fill="x")

        tk.Label(spacing_frame, bg=self.bg_color, fg=self.fg_color, text="Spacing:   x").pack(side="left", padx=(10,5), pady=10)
        
        self.spacing_x = tk.StringVar()
        self.spacing_x.set("0")
        spacing_x_entry = tk.Entry(spacing_frame, bg=self.field_bg, fg=self.fg_color, width=12, textvariable=self.spacing_x)
        spacing_x_entry.pack(side="left", pady=10)
        spacing_x_entry.bind("<FocusIn>", self.on_entry_FocusIn)
        spacing_x_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        ToolTip(spacing_x_entry, "How much horizontal space between each sprite?", False, True)

        tk.Label(spacing_frame, bg=self.bg_color, fg=self.fg_color, text="px   y").pack(side="left", padx=5, pady=10)

        self.spacing_y = tk.StringVar()
        self.spacing_y.set("0")
        spacing_y_entry = tk.Entry(spacing_frame, bg=self.field_bg, fg=self.fg_color, width=12, textvariable=self.spacing_y)
        spacing_y_entry.pack(side="left", pady=10)
        spacing_y_entry.bind("<FocusIn>", self.on_entry_FocusIn)
        spacing_y_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        ToolTip(spacing_y_entry, "How much vertical space between each sprite?", False, True)

        tk.Label(spacing_frame, bg=self.bg_color, fg=self.fg_color, text="px").pack(side="left", padx=(5,10), pady=10)

        # Preset Subframe

        preset_input_frame = tk.Frame(search_preset_subframe, bg=self.bg_color)
        preset_input_frame.pack(side="top", fill="x")

        tk.Label(preset_input_frame, bg=self.bg_color, fg=self.fg_color, text="Preset:").pack(side="left", padx=(10,5), pady=10)

        self.preset_path = tk.StringVar()
        preset_path_entry = tk.Entry(preset_input_frame, bg=self.field_bg, fg=self.fg_color, textvariable=self.preset_path)
        preset_path_entry.pack(side="left", pady=10, fill="x", expand=True)
        preset_path_entry.bind("<FocusIn>", self.on_entry_FocusIn)
        preset_path_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        ToolTip(preset_path_entry, "Enter the preset's path. (Preset should be a .json that contains pose data.)", False, True)

        def open_preset_json():
            path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("Json File", "*.json")])
            if path:
                self.preset_path.set(path)

        preset_pick_button = tk.Button(preset_input_frame, bg=self.button_bg, fg=self.fg_color, text="📁", command=open_preset_json)
        preset_pick_button.pack(side="left", padx=10, pady=10)
        ToolTip(preset_pick_button, "Choose a preset. (Preset should be a .json that contains pose data.)", False, True)

        # Search options

        search_options_frame = tk.Frame(self.right_frame, bg=self.bg_color, highlightthickness=1, highlightbackground=self.secondary_fg)
        search_options_frame.pack(side="top", fill="x")

        self.start_search_in_center = tk.BooleanVar()
        start_search_in_center_checkbutton = tk.Checkbutton(search_options_frame, text="Start search in center", bg=self.bg_color, fg=self.fg_color, selectcolor=self.button_bg, onvalue=True, offvalue=False, variable=self.start_search_in_center)
        start_search_in_center_checkbutton.pack(side="top", padx=5, pady=5)
        start_search_in_center_checkbutton.select()
        ToolTip(start_search_in_center_checkbutton, "When searching the spritesheet, the program will look at each row starting in the middle of the image, rather than at the edge.\nIt will search outward in one direction before reaching the edge, at which point it will search in the other direction, before moving onto the next row.\nRecommended for sprite sheets that group poses in a vertical formation, as it makes the order that pose images are found in much more intuitive. Not recommended if \"Search right-to-left\" is enabled.")
        
        self.search_right_to_left = tk.BooleanVar()
        search_right_to_left_checkbutton = tk.Checkbutton(search_options_frame, text="Search right-to-left", bg=self.bg_color, fg=self.fg_color, selectcolor=self.button_bg, onvalue=True, offvalue=False, variable=self.search_right_to_left)
        search_right_to_left_checkbutton.pack(side="top", padx=5, pady=5)
        ToolTip(search_right_to_left_checkbutton, "Search the spritesheet from right-to-left, instead of from left-to-right.\nRecommended if \"Start search in center\" is disabled, as most characters face right by default,\nand most sprite sheets show the rightmost sprites on the right side of the sheet, so the generated data will use the right-facing poses as the defaults.")

        self.padding_types = ["Show only always-visible pixels", "Show all theoretically-visible pixels", "None"]

        padding_label = tk.Label(search_options_frame, text="Automatic padding type:", bg=self.bg_color, fg=self.fg_color)
        padding_label.pack(side="top", padx=10, pady=10)
        # ToolTip(padding_label, "- Show only always-visible pixels: Padding for pose images will increase to show how much space is visible in all instances of that pose image. (Recommended)\n\n- Show all theoretically-visible pixels: Same as above, but padding also contains space that is not visible in some pose boxes.\n\n- None: No extra automatic padding is applied. Recommended if using the \"Custom padding\" option.")

        self.padding_type_option = tk.StringVar(value=self.padding_types[0])
        
        padding_type_optionmenu = tk.OptionMenu(search_options_frame, self.padding_type_option, *self.padding_types)
        padding_type_optionmenu.configure(bg=self.field_bg, fg=self.fg_color, activebackground=self.bg_color, activeforeground=self.fg_color, width=28, anchor="w", justify="left", highlightthickness=1, highlightbackground=self.secondary_fg, bd=0, relief="flat")
        padding_type_optionmenu["menu"].configure(bg=self.field_bg, fg=self.fg_color, activebackground=self.secondary_bg, activeforeground=self.fg_color)
        padding_type_optionmenu.pack(side="top", padx=5, pady=5)
        ToolTip(padding_type_optionmenu, "- Show only always-visible pixels: Padding for pose images will increase to show how much space is visible in all instances of that pose image. (Recommended)\n\n- Show all theoretically-visible pixels: Same as above, but padding also contains space that is not visible in some pose boxes.\n\n- None: No extra automatic padding is applied. Recommended if using the \"Custom padding\" option.")

        custom_padding_frame = tk.Frame(search_options_frame, bg=self.bg_color)
        custom_padding_frame.pack(side="top", padx=5, pady=5)

        tk.Label(custom_padding_frame, text="Custom padding amount:", bg=self.bg_color, fg=self.fg_color).pack(side="left", padx=(0,5))

        self.custom_padding = tk.IntVar()
        self.custom_padding.set(0)

        custom_padding_entry = tk.Entry(custom_padding_frame, bg=self.field_bg, fg=self.fg_color, textvariable=self.custom_padding, width=8) # string values will mess everything up!
        custom_padding_entry.pack(side="left", padx=(5,0))
        custom_padding_entry.bind("<FocusIn>", self.on_entry_FocusIn)
        custom_padding_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        ToolTip(custom_padding_entry, "Enter a custom amount of padding to apply to each pose image. If used alongside automatic padding, this will add the automatic and custom padding together.\n(Negative values are allowed, and will instead subtract from automatic padding without cutting off any of the pose images.)")

        self.generate_button = tk.Button(search_options_frame, text="Generate Pose Data...", command=self.generate_output, bg=self.button_bg, fg=self.fg_color)
        self.generate_button.pack(side="bottom", padx=5, pady=5)
        ToolTip(self.generate_button, "Generate data! (May take a while)", True, True)

        # TODO TODO TODO: some weird stuff with scrolling. i think the preview canvas scrollbar still scrolls the layer canvas

        self.bind_all("<Button-1>", on_global_click, add="+")

    def on_mousewheel(self, event):
        delta = -1 * (event.delta // 120)
        self.layer_canvas.yview_scroll(delta, "units")

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