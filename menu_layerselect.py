import os
# import io, os
import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox, ttk
# from PIL import Image, ImageTk, ImageOps
from PIL import Image, ImageTk
# from generate import GenerateJSON, generate_all
# from generate import generate_all
# from generate import generate_all, generate
from tooltip import ToolTip

from shared import on_global_click, consistxels_version

import threading

import json

# from listener import pipe_listener

import time

# import io, os
# from concurrent.futures import ProcessPoolExecutor
# from queue import Queue

# from multiprocessing import Process, Pipe
# from multiprocessing import Process, Queue, Pipe

import sys
import subprocess


import tempfile

class Menu_LayerSelect(tk.Frame):
    def __init__(self, master, show_frame_callback):
        super().__init__(master)

        # self.gen = gen

        # in the future, should be taken from some style file
        self.bg_color = "#2e2e2e"
        self.fg_color = "#ffffff"
        self.secondary_bg = "#3a3a3a"
        self.secondary_fg = "#6a6a6a"
        self.button_bg = "#444"
        self.field_bg = "#222222"

        # Track images and border
        self.layer_data = []  # List of dicts: {path, name, thumbnail, img_obj}
        self.border_image = None
        self.border_path = None
        self.border_color = "#00007f" # in the future, could be taken from info stored from last generation

        # self.root.configure(bg=self.bg_color)
        self.configure(bg=self.bg_color)

        # self.queue = Queue()
        # self.executor = ProcessPoolExecutor()

        # TODO TEMP GET RID OF
        # self.gen_proc = None
        # self.listener_proc= None
        self.process = None

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
        self.load_button = tk.Button(self.header, text="📁 Load", bg=self.button_bg, fg=self.fg_color, command=self.import_layer_select_json)
        self.load_button.pack(padx=(0,10), pady=10, side="left")
        ToolTip(self.load_button, "Load a .json file and restore previous search options and layer data.\n(Works with both of the previous 'Save' options, as well as generated pose data output.)")

        # New button
        self.new_button = tk.Button(self.header, text="➕ New", bg=self.button_bg, fg=self.fg_color)
        self.new_button.pack(padx=(0,10), pady=10, side="left")
        ToolTip(self.new_button, "Reset all options, delete all layers, and start from scratch.")

        # Header right:

        # Back button
        self.back_button = tk.Button(self.header, text="Back to Main Menu", bg=self.button_bg, fg=self.fg_color, command=lambda: show_frame_callback("Main"))
        self.back_button.pack(side="right", padx=10, pady=10)
        ToolTip(self.back_button, "...Come on, this one is self explanatory.", False, True, 2000)

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
        # (This would all look a LOT better if it was gridded rather than packed. look into it)

        # Grid frame
        grid_frame = tk.Frame(search_spacing_subframe, bg=self.bg_color)
        grid_frame.pack(side="top", fill="x")

        tk.Label(grid_frame, bg=self.bg_color, fg=self.fg_color, text="Grid:   Rows:").pack(side="left", padx=(10,5), pady=10)
        
        self.spacing_grid_rows = tk.StringVar()
        self.spacing_grid_rows.set("0")
        spacing_grid_rows_entry = tk.Entry(grid_frame, bg=self.field_bg, fg=self.fg_color, width=6, textvariable=self.spacing_grid_rows)
        spacing_grid_rows_entry.pack(side="left", pady=10)
        spacing_grid_rows_entry.bind("<FocusIn>", self.on_entry_FocusIn)
        spacing_grid_rows_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        ToolTip(spacing_grid_rows_entry, "How many rows does the sprite sheet have?", False, True)

        tk.Label(grid_frame, bg=self.bg_color, fg=self.fg_color, text="   Columns:").pack(side="left", padx=5, pady=10)

        self.spacing_grid_columns = tk.StringVar()
        self.spacing_grid_columns.set("0")
        spacing_grid_columns_entry = tk.Entry(grid_frame, bg=self.field_bg, fg=self.fg_color, width=6, textvariable=self.spacing_grid_columns)
        spacing_grid_columns_entry.pack(side="left", pady=10)
        spacing_grid_columns_entry.bind("<FocusIn>", self.on_entry_FocusIn)
        spacing_grid_columns_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        ToolTip(spacing_grid_columns_entry, "How many columns does the sprite sheet have?", False, True)

        # Outer padding
        spacing_padding_frame = tk.Frame(search_spacing_subframe, bg=self.bg_color)
        spacing_padding_frame.pack(side="top", fill="x")

        tk.Label(spacing_padding_frame, bg=self.bg_color, fg=self.fg_color, text="Padding:   Outer:").pack(side="left", padx=(10,5), pady=10)

        self.outer_padding = tk.StringVar()
        self.outer_padding.set("0")
        outer_padding_entry = tk.Entry(spacing_padding_frame, bg=self.field_bg, fg=self.fg_color, width=6, textvariable=self.outer_padding)
        outer_padding_entry.pack(side="left")
        outer_padding_entry.bind("<FocusIn>", self.on_entry_FocusIn)
        outer_padding_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        ToolTip(outer_padding_entry, "How much space between the sprites and the edge of the sprite sheet?\n(NOT to be confused with the automatic and custom padding - Outer and inner are\nfor the input images, automatic and custom are for the output images)", False, True)

        # tk.Label(spacing_padding_frame, bg=self.bg_color, fg=self.fg_color, text="px").pack(side="left", padx=(5,10), pady=10)

        # Inner padding
        # inner_padding_frame = tk.Frame(search_spacing_subframe, bg=self.bg_color)
        # inner_padding_frame.pack(side="top", fill="x")

        tk.Label(spacing_padding_frame, bg=self.bg_color, fg=self.fg_color, text="px   Inner:").pack(side="left", padx=5, pady=10)

        self.inner_padding = tk.StringVar()
        self.inner_padding.set("0")
        inner_padding_entry = tk.Entry(spacing_padding_frame, bg=self.field_bg, fg=self.fg_color, width=6, textvariable=self.inner_padding)
        inner_padding_entry.pack(side="left", pady=10)
        inner_padding_entry.bind("<FocusIn>", self.on_entry_FocusIn)
        inner_padding_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        ToolTip(inner_padding_entry, "How much extra padding around each sprite?\n(NOT to be confused with the automatic and custom padding - Outer and inner are\nfor the input images, automatic and custom are for the output images)", False, True)

        inner_px_label = tk.Label(spacing_padding_frame, bg=self.bg_color, fg=self.fg_color, text="px")
        inner_px_label.pack(side="left", padx=(5,10), pady=10)

        # Separation
        separation_frame = tk.Frame(search_spacing_subframe, bg=self.bg_color)
        separation_frame.pack(side="top", fill="x")

        tk.Label(separation_frame, bg=self.bg_color, fg=self.fg_color, text="Separation:   x").pack(side="left", padx=(10,5), pady=10)
        
        self.spacing_x_separation = tk.StringVar()
        self.spacing_x_separation.set("0")
        x_separation_entry = tk.Entry(separation_frame, bg=self.field_bg, fg=self.fg_color, width=6, textvariable=self.spacing_x_separation)
        x_separation_entry.pack(side="left", pady=10)
        x_separation_entry.bind("<FocusIn>", self.on_entry_FocusIn)
        x_separation_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        ToolTip(x_separation_entry, "How much horizontal space between each sprite?", False, True)

        tk.Label(separation_frame, bg=self.bg_color, fg=self.fg_color, text="px   y").pack(side="left", padx=5, pady=10)

        self.spacing_y_separation = tk.StringVar()
        self.spacing_y_separation.set("0")
        y_separation_entry = tk.Entry(separation_frame, bg=self.field_bg, fg=self.fg_color, width=6, textvariable=self.spacing_y_separation)
        y_separation_entry.pack(side="left", pady=10)
        y_separation_entry.bind("<FocusIn>", self.on_entry_FocusIn)
        y_separation_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        ToolTip(y_separation_entry, "How much vertical space between each sprite?", False, True)

        tk.Label(separation_frame, bg=self.bg_color, fg=self.fg_color, text="px").pack(side="left", padx=(5,10), pady=10)

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

        # detect identical images 
        # Check if poses use already-found pose images, so they can share the same pose image.\n(Highly recommended - this is kinda the whole point)
        
        # detect rotated images
        # Check if poses use rotated versions of already-found pose images.

        # detect horizontally mirrored images
        # Check if poses use horizontally-flipped versions of already-found pose images.
        
        # detect vertically mirrored images
        # Check if poses use vertically-flipped versions of already-found pose images.
        # 
        # (Automatically disabled when using both "detect rotated" and "detect hori. mirrored" to avoid redundancy;
        # a horizontally-flipped, 180-degrees-rotated image is identical to a vertically-flipped image.)

        # Generation

        # generate empty poses
        # Determine whether pose data will be created for completely-empty pose boxes.

        # export versions of layers with only unique pose images???
        # (might be good to have this as a setting here. i think so, at least)

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

        generate_frame = tk.Frame(self.right_frame, bg=self.bg_color, highlightthickness=1, highlightbackground=self.secondary_fg)
        generate_frame.pack(side="bottom", fill="both", expand=True)

        generate_options_frame = tk.Frame(generate_frame, bg=self.bg_color)
        generate_options_frame.pack(side="top")

        # checkboxes and entries and such

        generate_buttons_frame = tk.Frame(generate_frame, bg=self.bg_color)
        generate_buttons_frame.pack(side="left")

        # self.generate_button = tk.Button(search_options_frame, text="Generate Pose Data...", command=self.generate_output, bg=self.button_bg, fg=self.fg_color)
        # self.generate_button = tk.Button(search_options_frame, text="Generate Pose Data...", command=self.TEST_generate_button_pressed, bg=self.button_bg, fg=self.fg_color)
        self.generate_button = tk.Button(generate_buttons_frame, text="Generate Pose Data...", command=self.TEST_generate_button_pressed, bg=self.button_bg, fg=self.fg_color)
        self.generate_button.pack(side="top", padx=10, pady=10)
        # self.generate_button.grid(padx=10, pady=10, row=0, column=0)
        ToolTip(self.generate_button, "Generate data! (May take a while)", True, True)

        # for safety i guess
        self.generate_process = None

        # disable if no process!!!
        self.cancel_button = tk.Button(generate_buttons_frame, text="Cancel", command=self.cancel_process, fg="#dd5555", bg=self.button_bg, state="disabled")
        self.cancel_button.pack(side="top", padx=10, pady=(0,10), fill="x")
        # self.cancel_button.grid(padx=10, pady=(0,10), row=1, column=0)
        # TODO add tooltip

        generate_progress_frame = tk.Frame(generate_frame, bg=self.bg_color)
        generate_progress_frame.pack(side="left", fill="x", expand=True)

        self.progress_header_label = tk.Label(generate_progress_frame, bg=self.bg_color, fg=self.fg_color)
        self.progress_header_label.pack(side="top", padx=(0,10), pady=(10,0), fill="x", expand=True)

        # self.progress_label = tk.Label(search_options_frame, bg=self.bg_color, fg=self.fg_color, text="")
        self.progress_info_label = tk.Label(generate_progress_frame, bg=self.bg_color, fg=self.fg_color)
        self.progress_info_label.pack(side="top", padx=(0,10), pady=(0,5), fill="x", expand=True)
        # self.progress_label.grid(padx=10, pady=10, row=0, column=1, columnspan=2)

        # self.progress_bar = ttk.Progressbar(search_options_frame, orient="horizontal", maximum=100)
        self.progress_bar = ttk.Progressbar(generate_progress_frame, orient="horizontal", maximum=100)
        self.progress_bar.pack(padx=(0,10), pady=(0,10), side="top", fill="x", expand=True)
        # self.progress_label.grid(padx=10, pady=10, row=1, column=1, columnspan=2)

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

            if len(self.layer_data):
                if self.layer_data[0]["img"].size != image.size:
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
            self.layer_data.append({"path": path, "name": name, "img": image, "thumb": photo, "alt_source": alt_source})
        
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

            if len(self.layer_data):
                if self.layer_data[0]["img"].size != temp_border_image.size:
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
        if 0 <= new_index < len(self.layer_data):
            self.layer_data[index], self.layer_data[new_index] = self.layer_data[new_index], self.layer_data[index]
            self.redraw_image_entries()
            # self.update_preview()
            self.update_preview_button.configure(bg="#ffff00", fg="#000000")

    def delete_image(self, index):
        # close image
        self.layer_data[index]["img"].close()

        del self.layer_data[index]
        self.redraw_image_entries()
        # self.update_preview()
        self.update_preview_button.configure(bg="#ffff00", fg="#000000")

    def redraw_image_entries(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for i, data in enumerate(self.layer_data):
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
            self.layer_data[index]["alt_source"] = path
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
        for item in reversed(self.layer_data):
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

            for image in self.layer_data:
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
        for data in self.layer_data:
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

            # GenerateJSON(name, self.border_path, self.border_color, image_info, self.start_search_in_center.get(), self.search_right_to_left.get(), padding_type, self.custom_padding.get())
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
    
    def compile_data_into_dict(self):
        header = {
            "name": self.name_entry_input.get(),
            "consistxels_version": consistxels_version,
            "paths_are_local": True, # CHANGE! Or i guess not HERE, this only really applies to saved layer data and all that
            "width": None, # get this figured out sooner probably?
            "height": None # get this figured out sooner probably?
        }

        search_data = {
            "start_search_in_center": self.start_search_in_center.get(),
            "search_right_to_left": self.search_right_to_left.get(),
            "detect_identical_images": True, # TODO
            "detect_rotated_images": True, # TODO
            "detect_flip_h_images": True, # TODO
            "detect_flip_v_images": False # TODO
        }

        search_type_data = {
            "search_type": self.search_type_option.get(),
            "border_color": self.border_color,
            "spacing_rows": self.spacing_grid_rows.get(), # TODO: change so can only be int
            "spacing_columns": self.spacing_grid_columns.get(), # TODO: change so can only be int
            "spacing_outer_padding": self.outer_padding.get(), # TODO: change so can only be int
            "spacing_inner_padding": self.inner_padding.get(), # TODO: change so can only be int
            "spacing_x_separation": self.spacing_x_separation.get(), # TODO: change so can only be int
            "spacing_y_separation": self.spacing_y_separation.get() # TODO: change so can only be int
        }

        generation_data = {
            "automatic_padding_type": self.padding_type_option.get(), # TODO: change so can only be int
            "custom_padding_amount": self.custom_padding.get(), # TODO: change so can only be int
            "generate_empty_poses": False # TODO
        }

        # TODO: A LOT
        layer_data = []
        duplicate_layer_name = False
        for layer in self.layer_data:
            if layer["name"] in [image["name"] for image in layer_data]:
                duplicate_layer_name = True
                break
            # layer_data.append({"path": layer["path"], "name": layer["name"], "alt_source": layer["alt_source"]})
            layer_data.append({ # TODO TODO TODO
                "name": layer["name"], "is_border": False, "is_cosmetic_only": False,
                "search_image_path": layer["path"], "source_image_path": layer["alt_source"],
                "export_original_images": True
            })

        if search_type_data["search_type"] == "Border": # TODO. can mostly just copy-and-paste this. still do want rigid control of the data in the border layer
            layer_data.append({
                "name": "border", "is_border": True, "is_cosmetic_only": True,
                "search_image_path": self.border_path, "source_image_path": None,
                "export_original_images": True
                
            })

        pose_data = None
        if self.search_type_option.get() == "Preset":
            pass # TODO
        
        data = {
            "header": header, "search_data": search_data, "search_type_data": search_type_data,
            "generation_data": generation_data, "layer_data": layer_data, "pose_data": pose_data
        }
        
        return data

    def TEST_generate_button_pressed(self):
        pass

        # warning stuff

        # def update_progress(new_value = None, progress_text = None):
        #     if new_value != None:
        #         self.progress_bar["value"] = new_value
        #     else:
        #         self.progress_bar["value"] = self.progress_bar["value"] # these FEEL unnecessary, but progress_label didnt work without one. idk

        #     if progress_text != None:
        #         self.progress_label.configure(text=progress_text)
        #     else:
        #         self.progress_label.configure(text=self.progress_label.cget("text"))

        # test data
        # TEMP_header = {
        #     "name": "TEST",
        #     "consistxels_version": "0.1",
        #     # "time_to_generate": None, # MAYBE?
        #     "paths_are_local": True
        # }

        # TEMP_layer_data = [
        #     {"name": "closearm", "is_border": False, "is_cosmetic_only": True, "search_image_path": "closearm.png", "source_image_path": "closearm.png", "export_original_images": False},
        #     {"name": "farleg", "is_border": False, "is_cosmetic_only": False, "search_image_path": None, "source_image_path": None, "export_original_images": True},
        #     {"name": "border", "is_border": True, "is_cosmetic_only": True, "search_image_path": "border.png", "source_image_path": None, "export_original_images": True}
        # ]

        # TEMP_search_data = {
        #     "start_search_in_center": True,
        #     "search_right_to_left": False,
        #     "detect_identical_images": True, # should we default the other searches to False if this is false? i dunno
        #     "detect_rotated_images": True,
        #     "detect_flip_h_images": True,
        #     # "detect_flip_v_images": False # TECHNICALLY, we could just store this info in flip_h and rotated. DEFINITELY DOABLE. i'll think abt it
        # }

        # TEMP_search_type_data = {
        #     "search_type": "Border",
        #     # "border_layer_index": 2, # do we wanna do this? or do we wanna do a more automatic approach? probably the auto one
        #     "border_color": "#00007f",
        #     "spacing_rows": None,
        #     "spacing_columns": None,
        #     "spacing_outer_padding": None,
        #     "spacing_inner_padding": None,
        #     "spacing_x_separation": None,
        #     "spacing_y_separation": None
        # }

        # TEMP_generation_data = {
        #     "automatic_padding_type": "None",
        #     "custom_padding_amount": 0,
        #     "generate_empty_poses": False
        #     # likely some other stuff eventually, i guess like palette stuff??? i dunno
        # }

        # TEMP_pose_data = [
        #     {
        #         "name": "pose_0_0", "x_position": 0, "y_position": 0,
        #         "width": 0, "height": 0,
        #         "limb_data":[
        #             {
        #                 "name": "closearm", "layer_index": 0,
        #                 "x_offset": 0, "y_offset": 0, "image_index": 0,
        #                 "rotation": 0, "flip_h": False, "flip_v": False
        #             }
        #         ]
        #     }
        # ]

        header = {
            "name": self.name_entry_input.get(),
            "consistxels_version": consistxels_version,
            "paths_are_local": True, # CHANGE! Or i guess not HERE, this only really applies to saved layer data and all that
            "width": None, # get this figured out sooner probably?
            "height": None # get this figured out sooner probably?
        }

        search_data = {
            "start_search_in_center": self.start_search_in_center.get(),
            "search_right_to_left": self.search_right_to_left.get(),
            "detect_identical_images": True, # TODO
            "detect_rotated_images": True, # TODO
            "detect_flip_h_images": True, # TODO
            "detect_flip_v_images": False # TODO
        }

        search_type_data = {
            "search_type": self.search_type_option.get(),
            "border_color": self.border_color,
            "spacing_rows": self.spacing_grid_rows.get(), # TODO: change so can only be int
            "spacing_columns": self.spacing_grid_columns.get(), # TODO: change so can only be int
            "spacing_outer_padding": self.outer_padding.get(), # TODO: change so can only be int
            "spacing_inner_padding": self.inner_padding.get(), # TODO: change so can only be int
            "spacing_x_separation": self.spacing_x_separation.get(), # TODO: change so can only be int
            "spacing_y_separation": self.spacing_y_separation.get() # TODO: change so can only be int
        }

        generation_data = {
            "automatic_padding_type": self.padding_type_option.get(), # TODO: change so can only be int
            "custom_padding_amount": self.custom_padding.get(), # TODO: change so can only be int
            "generate_empty_poses": False # TODO
        }

        # TODO: A LOT
        layer_data = []
        duplicate_layer_name = False
        for layer in self.layer_data:
            if layer["name"] in [image["name"] for image in layer_data]:
                duplicate_layer_name = True
                break
            # layer_data.append({"path": layer["path"], "name": layer["name"], "alt_source": layer["alt_source"]})
            layer_data.append({ # TODO TODO TODO
                "name": layer["name"], "is_border": False, "is_cosmetic_only": False,
                "search_image_path": layer["path"], "source_image_path": layer["alt_source"],
                "export_original_images": True
            })

        if search_type_data["search_type"] == "Border": # TODO. can mostly just copy-and-paste this. still do want rigid control of the data in the border layer
            layer_data.append({
                "name": "border", "is_border": True, "is_cosmetic_only": True,
                "search_image_path": self.border_path, "source_image_path": None,
                "export_original_images": True
                
            })

        pose_data = None
        if self.search_type_option.get() == "Preset":
            pass # TODO
        
        data = {
            "header": header, "search_data": search_data, "search_type_data": search_type_data,
            "generation_data": generation_data, "layer_data": layer_data, "pose_data": pose_data
        }

        # TEMP_data = {"header": TEMP_header, "search_data": TEMP_search_data, "search_type_data": TEMP_search_type_data, "generation_data": TEMP_generation_data, "layer_data": TEMP_layer_data}

        # check for output folder in entry, when I get around to adding it
        TEMP_output_folder_path = filedialog.askdirectory(title="Select an output folder")

        if len(layer_data) > 0 and header["name"] != "" and not duplicate_layer_name and TEMP_output_folder_path:
            # disable start button, enable cancel button

            # def TEST_generate_output():
                # generate_all(TEMP_data, TEMP_output_folder_path, update_progress)
                # generate_all(data, TEMP_output_folder_path, lambda new_value, progress_text: self.after(0, update_progress, new_value, progress_text))
                # generate_all(data, TEMP_output_folder_path, None)

            # call the thingy!
            # threading.Thread(target=TEST_generate_output, daemon=True).start()

            # when everything's complete, convert bytes to images, save 'em, re-enable gui

            # parent_conn, child_conn = Pipe(False)
            # self.parent_conn, self.child_conn = Pipe()
            # self.generate_process = Process(target=generate_all, args=(data, TEMP_output_folder_path, self.child_conn))
            # self.generate_process.start()

            # self.gui_queue, self.gen_proc, self.listener_proc = 
            # self.start_processes(data, TEMP_output_folder_path)
            # self.poll_queue()

            # occasionally poll pipe for updates
            try:
                # self.generate_button.configure(state="disabled")
                # self.load_button.configure(state="disabled")
                # self.new_button.configure(state="disabled")
                # self.back_button.configure(state="disabled")
                # self.cancel_button.configure(state="normal")

                # self.after(100, lambda: self.check_pipe(parent_conn))
                
                # threading.Thread(target=self.after, args=(100, lambda: self.check_pipe(parent_conn)), daemon=True).start()
                # threading.Thread(target=self.check_pipe, args=[self.parent_conn], daemon=True).start()

                # gui_queue, gen_proc, listener_proc = start_processes()
                # self.start_processes()


                # self.start_process(data, TEMP_output_folder_path)

                # self.gen(data, TEMP_output_folder_path, self.update_progress)
                # self.gen(data, TEMP_output_folder_path, None)

                temp_json_data = {"data": data, "path": TEMP_output_folder_path}
                # temp_json_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode='w')
                # json.dump(temp_json_data, temp_json_file)

                # # print(["generate", temp_json_file.name.replace('\\', '/')])
                # print(json.dumps({"type": "generate", "val": temp_json_file.name.replace('\\', '/')}), flush=True)
                # temp_json_file.close()


                with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_json_file:
                    json.dump(temp_json_data, temp_json_file)
                    print(json.dumps({"type": "generate", "val": temp_json_file.name.replace('\\', '/')}), flush=True)

            except Exception as e:
                pass
                # self.cancel_process()
                # print("exception starting thread:", e)
                print(json.dumps({"type": "error", "val": e}), flush=True)
        else:
            warning_output = ""

            # if self.border_path == None: warning_output += "Please add a border image"
            if len(layer_data) <= 0:
                if warning_output != "": warning_output += "\n"
                warning_output += "Please add at least one layer"
            if header["name"] == "":
                if warning_output != "": warning_output += "\n"
                warning_output += "Please enter a name for this sprite sheet"
            if duplicate_layer_name:
                if warning_output != "": warning_output += "\n"
                warning_output += "Ensure all layers have unique names"
            if not TEMP_output_folder_path:
                if warning_output != "": warning_output += "\n"
                warning_output += "You must select an output folder first"

            messagebox.showwarning("Wait!", warning_output)

    # # I DONT GET IT
    # def check_queue(self):
    #     while not self.queue.empty():
    #         result = self.queue.get()
    #         if result == "DONE":
    #             pass
    #             # end_generation() function or something
    #             return
            

    #         # update progressbar here

    #         # save results
        
    #     self.after(100, self.check_queue)

    # def check_pipe_thread(self):
    #     while True:
    #         if self.parent_conn.poll():
    #             msg = self.parent_conn.recv()
    #             self.after(0, lambda m=msg: self.handle_message(m))
    #         time.sleep(0.05)

    # def check_pipe(self, parent_conn):
    #     while True:
    #         latest_message = None
    #         try:
    #             while parent_conn.poll(): # drain the pipe
    #                 try:
    #                     latest_message = parent_conn.recv()
    #                 except EOFError:
    #                     break
    #         except (OSError, EOFError):
    #             # Pipe is already closed — do nothing, stop polling

    #             # latest_message = "done" # a bit clumsy, presumably, because it doesn't actually KNOW that it's done

    #             raise Exception
    #             # return

    #         if latest_message != None:
    #             if latest_message[0] == "done":
    #                 # show that process is complete
    #                 self.progress_bar["value"] = latest_message[1]
    #                 self.progress_header_label.configure(text=latest_message[2])
    #                 self.progress_info_label.configure(text=latest_message[3])

    #                 messagebox.showinfo(latest_message[2], latest_message[3])

    #                 parent_conn.send("ack")
                    
    #                 self.generate_process = None

    #                 self.process_ended()
    #                 return
    #             elif latest_message[0] == "update":
    #                 # if self.winfo_toplevel().focus_get() != None:
    #                     self.progress_bar["value"] = latest_message[1]
    #                     self.progress_header_label.configure(text=latest_message[2])
    #                     self.progress_info_label.configure(text=latest_message[3])
    #             elif latest_message[0] == "error":
    #                 print("error:", latest_message[1])
    #                 self.process_ended()
    #                 return
    #             else: print("unhandled message:", latest_message)
                
    #         time.sleep(0.1)
    #         # self.after(1000 if self.winfo_toplevel().focus_get() != None else 100, lambda: self.check_pipe(parent_conn))
    #         # print(self.winfo_toplevel().focus_get())
    #         # self.after(100, lambda: self.check_pipe(parent_conn))
    
    def cancel_process(self):
        print(json.dumps({"type": "cancel"}), flush=True)
    #     if not app_closing:
    #         self.progress_header_label.configure(text="")
    #         self.progress_info_label.configure(text="Cancelled")
    #         self.process_ended()

    #     # will REALLY need to check this
    #     if self.process != None:
    #         if self.process.poll():
    #             self.process.terminate()
    #             # self.process.join()
    #             self.process.stdout.close()
    #             self.process.stderr.close()

    #         # self.process = None
    #         if self.process.poll():
    #             raise Exception

        # if self.gen_proc != None:
        #     if self.gen_proc.is_alive():
        #         self.gen_proc.terminate()
        #         self.gen_proc.join()
        #     self.gen_proc = None

        # if self.listener_proc != None:
        #     if self.listener_proc.is_alive():
        #         self.listener_proc.terminate()
        #         self.listener_proc.join()

        #     self.listener_proc = None
        


        # if self.generate_process != None:

        #     if self.generate_process.is_alive():
        #         self.generate_process.terminate()
        #         self.generate_process.join()

        #         if not app_closing: self.progress_header_label.configure(text="Cancelled")
        #     else:
        #         if not app_closing: self.progress_header_label.configure(text="Process already terminated")
            
        #     if not app_closing: self.generate_process = None
        # else:
        #     pass # maybe throw error. or maybe not? idk

        # if not app_closing:
        #     self.process_ended()
        #     self.progress_bar["value"] = 0
        #     self.progress_info_label.configure(text="")
    
    def generate_begin(self):
        self.generate_button.configure(state="disabled")
        self.load_button.configure(state="disabled")
        self.new_button.configure(state="disabled")
        self.back_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")

    def generate_end(self):
        self.generate_button.configure(state="normal")
        self.load_button.configure(state="normal")
        self.new_button.configure(state="normal")
        self.back_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")


    # def start_processes(self, data, TEMP_output_folder_path):
    #     parent_conn, child_conn = Pipe()
    #     self.gui_queue = Queue()

    #     # gen_proc = Process(target=generate, args=(child_conn,))
    #     self.gen_proc = Process(target=generate_all, args=(data, TEMP_output_folder_path, child_conn))
    #     self.listener_proc = Process(target=pipe_listener, args=(parent_conn, self.gui_queue))

    #     self.gen_proc.start()
    #     self.listener_proc.start()

        # return gen_proc, listener_proc

    # def poll_queue(self):
    #     if self.winfo_toplevel().focus_get() != None:
    #         while not self.gui_queue.empty():
    #             msg = self.gui_queue.get()
    #             if msg[0] == "update":
    #                 self.progress_bar["value"] = msg[1]
    #                 self.progress_header_label.configure(text=msg[2])
    #                 self.progress_info_label.configure(text=msg[3])
    #             elif msg[0] == "done":
    #                 self.progress_bar["value"] = msg[1]
    #                 self.progress_header_label.configure(text=msg[2])
    #                 self.progress_info_label.configure(text=msg[3])

    #                 self.process_ended()
    #                 return

    #     self.after(1000 if self.winfo_toplevel().focus_get() == None else 100, self.poll_queue)


    # def start_process(self, data, path):
    #     # print("got to self.start_process()")
    #     self.generate_button.configure(state="disabled")
    #     self.load_button.configure(state="disabled")
    #     self.new_button.configure(state="disabled")
    #     self.back_button.configure(state="disabled")
    #     self.cancel_button.configure(state="normal")

    #     self.update_progress(0, "", "Initializing...")

    #     temp_json_data = {"data": data, "path": path}
    #     # print("temp_json_data initialized")
    #     temp_json_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode='w')
    #     # print("temp_json_file initialized")
    #     json.dump(temp_json_data, temp_json_file)
    #     # print("temp_json_data dumped into temp_json_file")
    #     temp_json_file.close()
    #     # print("temp_json_file closed")

    #     env = os.environ.copy()
    #     env["PYTHONUNBUFFERED"] = "1"

    #     self.process = subprocess.Popen(
    #         [sys.executable, "-u", "generate_worker.py", temp_json_file.name],
    #         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    #         # creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
    #         creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS | subprocess.HIGH_PRIORITY_CLASS | subprocess.CREATE_BREAKAWAY_FROM_JOB,
    #         env=env
    #     )
    #     # print("self.process created")

    #     self.most_recent_line = None

    #     threading.Thread(target=self.read_process_stdout, daemon=True).start()
    #     threading.Thread(target=self.check_most_recent_line, daemon=True).start()
    #     # print("read_process_stdout started")

    # #     # self.after(100, self.read_process_stdout)

    # def read_process_stdout(self):
    #     # print("got to self.read_process_stdout()")

    #     # latest_line = None
    #     # for line in self.process.stdout:
    #     #     latest_line = line
        
    #     # latest_line = latest_line.strip()

    #     # try:
    #     #     data = json.loads(line)
                
    #     #     if self.winfo_toplevel().focus_get() != None:
    #     #         status = data.get("status")
    #     #         value = data.get("value")
    #     #         header_text = data.get("header_text")
    #     #         info_text = data.get("info_text")

    #     #         # Update the GUI in the main thread
    #     #         self.after(0, self.update_progress, value, header_text, info_text)

    #     #     match status:
    #     #         case "update":
    #     #             pass
    #     #         case "error":
    #     #             messagebox.showerror(header_text, info_text)
    #     #             # self.process_ended()
    #     #             self.cancel_process(True)
    #     #             self.process_ended()
    #     #             # raise Exception
    #     #         case "done":
    #     #             messagebox.showinfo(header_text, info_text)
    #     #             # self.process_ended()
    #     #             self.cancel_process(True)
    #     #             self.process_ended()
    #     #             return
    #     # except json.JSONDecodeError:
    #     #     print("Malformed output:", line)
        
    #     # self.after(100, self.read_process_stdout)

    #     for line in self.process.stdout:
    #         line = line.strip()
    #         self.most_recent_line = line
            
    #         # time.sleep(0.05)
    
    # def check_most_recent_line(self):
    #     if self.most_recent_line:
    #         try:
    #             # line = self.process_output_buffer[-1]
    #             line = self.most_recent_line

    #             data = json.loads(line)
    #             status = data.get("status")
    #             header_text = data.get("header_text")
    #             info_text = data.get("info_text")
    #             value = data.get("value")
                
    #             match status:
    #                 case "update":
    #                     if self.winfo_toplevel().focus_get() != None:
    #                         # Update the GUI in the main thread
    #                         self.after(0, self.update_progress, value, header_text, info_text)
    #                 case "error":
    #                     self.process_ended()
    #                     self.after(0, self.update_progress, value, header_text, info_text)
    #                     messagebox.showerror(header_text, info_text)
    #                     # self.process_ended()
    #                     self.cancel_process(True)
    #                     # raise Exception
    #                     return
    #                 case "done":
    #                     self.process_ended()
    #                     self.after(0, self.update_progress, value, header_text, info_text)
    #                     messagebox.showinfo(header_text, info_text)
    #                     # self.process_ended()
    #                     self.cancel_process(True)
    #                     return
    #                 case "print":
    #                     print(info_text)
    #         except json.JSONDecodeError:
    #             print("Malformed output:", line)

    #     # print("gothere")
    #     self.after(100, self.check_most_recent_line)
    
    def update_progress(self, value, header_text, info_text):
        self.progress_bar["value"] = value
        self.progress_header_label.configure(text=header_text)
        self.progress_info_label.configure(text=info_text)
