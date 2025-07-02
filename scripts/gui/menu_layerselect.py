# TODO TODO TODO: go through and remove unnecessary frames that were there for formatting. can often use 'anchor="w"'

import os
import json
import tempfile
import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox, ttk
from PIL import Image, ImageTk, ImageColor

from scripts.classes.tooltip import ToolTip
from scripts.classes.viewport_canvas import ViewportCanvas
import scripts.gui.gui_shared as gui_shared
from scripts.gui.gui_shared import add_widget
from scripts.shared import consistxels_version

# Menu for selecting layers and options in order to generate sprite sheet data
class Menu_LayerSelect(tk.Frame):
    def __init__(self, master, change_menu_callback, set_unsaved_changes_callback, load_path = None):
        super().__init__(master) # Initialize menu's tkinter widget

        self.layer_data = []  # List of dicts: {name, search_image_path, source_image_path, is_border, is_cosmetic_only, export_layer_images}
        self.border_color = "#00007f" # TODO in the future, could be taken from info stored from last generation # ALSO could be a tk.StringVar()
        self.image_size = None # For creating preview image / generating pose images(?) TODO verify
        self.preview_image = None # Preview containing layer search images
        self.set_unsaved_changes_callback = set_unsaved_changes_callback # Sets a var in gui.py, which asks user before changing menu / exiting window if unsaved changes exist

        self.configure(bg=gui_shared.bg_color) # Change bg color

        self.after(0, self.setup_ui, change_menu_callback, load_path) # .setup_ui() in .after() to prevent ugly flickering
    
    # What it says on the tin
    def setup_ui(self, change_menu_callback, load_path = None):

        # Header
        self.header = tk.Frame(self, bg=gui_shared.bg_color)
        self.header.pack(fill="x", padx=2)
        
        # Header left:

        # Save button
        save_json_button = tk.Button(self.header, text="💾 Save .json", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=self.export_layerselect_json)
        save_json_button.pack(padx=10, pady=10, side="left")
        ToolTip(save_json_button,"""Save the selected search options and layer data to a .json file for later use. Should ONLY be used locally, and not transferred to other devices, as this uses direct paths to layer images that are specific to this device.""")

        # Save folder button (would like to save to .zip at some point to make it more obvious what this feature is for)
        save_folder_button = tk.Button(self.header, text="💾 Save all to folder", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=self.export_layerselect_all)
        save_folder_button.pack(padx=(0,10), pady=10, side="left")
        ToolTip(save_folder_button, """Save the selected search options, layer data, and layer images to a specified folder. This avoids the problem with the 'Save .json' option, and the folder can be transferred to other devices without issue.\n\n(It's recommended that you choose a new, EMPTY folder, so as to not clutter up your files!)""")
        
        # Load button
        self.load_button = tk.Button(self.header, text="📁 Load", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=self.import_layerselect_json)
        self.load_button.pack(padx=(0,10), pady=10, side="left")
        ToolTip(self.load_button, """Load a .json file and restore previous search options and layer data.\n\n(Works with both of the previous 'Save' options, as well as generated sheet data output.)""")

        # Clear button
        self.clear_button = tk.Button(self.header, text="✏️ Clear", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=lambda: change_menu_callback("LayerSelect"))
        self.clear_button.pack(padx=(0,10), pady=10, side="left")
        ToolTip(self.clear_button, "Reset all options, delete all layers, and start from scratch.")

        # Header right:

        # Back button
        self.back_button = tk.Button(self.header, text="Back to Main Menu", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=lambda: change_menu_callback("Main"))
        self.back_button.pack(side="right", padx=10, pady=10)
        ToolTip(self.back_button, "...Come on, this one is self explanatory.", False, True, 2000)

        # Main frame
        self.main_frame = tk.Frame(self, bg=gui_shared.bg_color)
        self.main_frame.pack(fill="both", expand=True)

        # Paned window to allow resizing of different submenus
        paned_window = tk.PanedWindow(self.main_frame, bg=gui_shared.bg_color, opaqueresize=False, sashrelief="flat", sashwidth=16, bd=0)
        paned_window.pack(fill="both", expand=True)

        # Left frame
        self.left_frame = tk.Frame(paned_window, bg=gui_shared.bg_color, width=480, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        self.left_frame.pack(side="left", fill="y", padx=10)
        self.left_frame.pack_propagate(False)

        # Center frame
        self.center_frame = tk.Frame(paned_window, bg=gui_shared.field_bg, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        self.center_frame.pack(side="right", fill="both", padx=10, expand=True)

        # Right frame
        self.right_frame = tk.Frame(paned_window, bg=gui_shared.bg_color, width=600, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        self.right_frame.pack(side="right", fill="y", padx=10)
        self.right_frame.pack_propagate(False)

        # Add left, center, and right frames to paned window
        paned_window.add(self.left_frame, minsize=417, stretch="never")
        paned_window.add(self.center_frame, minsize=2, stretch="always") # When entire window's size is changed, center frame is the only one that stretches/contracts
        paned_window.add(self.right_frame, minsize=400, stretch="never")
        
        # Layer options:

        # Layer header
        layer_header = tk.Frame(self.left_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        layer_header.pack(side="top", fill="x")

        # Layer main frame
        layer_main_frame = tk.Frame(self.left_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        layer_main_frame.pack(side="top", fill="both", expand=True)

        # Actual layer menu
        self.layer_canvas_frame = tk.Frame(layer_main_frame, bg=gui_shared.bg_color, width=0)
        self.layer_canvas_frame.pack(side="left", fill="both", expand=True)
        
        # Canvas containing layer option cards
        self.layer_canvas = tk.Canvas(self.layer_canvas_frame, bg=gui_shared.bg_color, highlightthickness=0, width=0)
        self.layer_canvas.pack(side="left", fill="both", expand=True)

        # Canvas's respective scrollbar
        self.layer_scrollbar = tk.Scrollbar(layer_main_frame, orient="vertical", command=self.layer_canvas.yview)
        self.layer_scrollbar.pack(side="left", fill="y", padx=(2,0))

        # Frame that scrolls inside the canvas
        self.scrollable_frame = tk.Frame(self.layer_canvas, bg=gui_shared.bg_color)
        self.scrollable_frame.bind("<Configure>", lambda e: self.layer_canvas.configure(scrollregion=self.layer_canvas.bbox("all")))

        # Create canvas in which to show layer info
        self.layer_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.layer_canvas.configure(yscrollcommand=self.layer_scrollbar.set)

        # Resize the scrollable frame and the layer card widths
        def resize_layer_scrollable_frame(_ = None):
            for i in range(len(self.layer_data)):
                self.update_layer_card_width(i)

        # Bind function to left frame. (TODO: this runs every time the window's modified at all, which is annoying. Try to see if this can be avoided)
        self.left_frame.bind("<Configure>", resize_layer_scrollable_frame)

        # Layer footer
        layer_footer = tk.Frame(self.left_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        layer_footer.pack(side="top", fill="x")

        # Top add buttons
        # Blank layer
        layer_add_blank_top = tk.Button(layer_header, text="➕ Blank layer", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=lambda t=True: self.add_blank_layer(t))
        layer_add_blank_top.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        ToolTip(layer_add_blank_top, "Add a blank layer as the top layer.")
        # From images
        layer_add_images_top = tk.Button(layer_header, text="➕ From image(s)", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=lambda t=True: self.add_image_layers(add_to_top=t))
        layer_add_images_top.pack(side="right", padx=(0,10), pady=10, fill="x", expand=True)
        ToolTip(layer_add_images_top, "Add image(s) as the top layer(s). Layer's name will be autofilled with its image's filename.")

        # Bottom add buttons
        # Blank layer
        layer_add_blank_bottom = tk.Button(layer_footer, text="➕ Blank layer", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=lambda t=False: self.add_blank_layer(t))
        layer_add_blank_bottom.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        ToolTip(layer_add_blank_bottom, "Add a blank layer as the bottom layer.", True)
        # From images
        layer_add_images_bottom = tk.Button(layer_footer, text="➕ From image(s)", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=lambda t=False: self.add_image_layers(add_to_top=t))
        layer_add_images_bottom.pack(side="right", padx=(0,10), pady=10, fill="x", expand=True)
        ToolTip(layer_add_images_bottom, "Add image(s) as the bottom layer(s). Layer's name will be autofilled with its image's filename.", True)
        
        # Bind scrolling to left frame
        gui_shared.bind_event_to_all_children(self.left_frame,"<MouseWheel>",self._on_left_frame_mousewheel)

        # Center preview:

        preview_frame = tk.Frame(self.center_frame, bg=gui_shared.field_bg, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        preview_frame.pack(side="top", fill="both", expand=True)

        preview_frame.grid_rowconfigure(0, weight=1) # For formatting canvas relative to the scrollbars
        preview_frame.grid_columnconfigure(0, weight=1)

        # 'ViewportCanvas' that displays an image more dynamically and intuitively, allowing panning, zooming, etc. without performance loss
        self.preview_viewportcanvas = ViewportCanvas(preview_frame, bg=gui_shared.field_bg, highlightthickness=0) # TODO move highlightthickness into ViewportCanvas declaration maybe? might be nice
        self.preview_viewportcanvas.grid(row=0, column=0, sticky="NSEW")

        # Preview scrollbars (TODO: somewhat nonfunctional due to bad math(?) in ViewportCanvas, but they at least LOOK right)
        preview_canvas_hori_scroll = tk.Scrollbar(preview_frame, orient="horizontal", command=self.preview_viewportcanvas.scroll_x)
        preview_canvas_hori_scroll.grid(row=1, column=0, sticky="EW")
        preview_canvas_vert_scroll = tk.Scrollbar(preview_frame, orient="vertical", command=self.preview_viewportcanvas.scroll_y)
        preview_canvas_vert_scroll.grid(row=0, column=1, sticky="NS")

        self.preview_viewportcanvas.connect_scrollbars(preview_canvas_hori_scroll, preview_canvas_vert_scroll) # Connect scrollbars to ViewportCanvas

        # Frame containing preview control buttons. Will likely have more added at some point
        canvas_buttons_frame = tk.Frame(self.center_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        canvas_buttons_frame.pack(side="top", fill="x")

        # Bottomleft reload button
        self.update_preview_button = tk.Button(canvas_buttons_frame, text="Update Preview", command=self.update_preview_image, bg=gui_shared.button_bg, fg=gui_shared.fg_color)
        self.update_preview_button.pack(side="left", padx=10, pady=10) # figure out how to get bottom-left
        ToolTip(self.update_preview_button, """Update the preview image that contains all layers ordered as shown. May take a while if you have a lot of images.\n\n(If the button is yellow, changes have been made, and the preview can be updated.)""", True)

        # To add:
        #   - Label/entry w/ current zoom level?
        #   - OptionMenu to select either search image preview or source image preview?
        #   - Maybe another option if preset pose data is being used? Kinda overstepping into generate.py's territory there

        # Right menu:

        # I want to find a way to make this more prominent somehow. It's VERY important and shouldn't be missed.
        name_frame = tk.Frame(self.right_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        name_frame.pack(side="top", fill="x")

        name_label = tk.Label(name_frame, text="Sprite sheet name:", bg=gui_shared.bg_color, fg=gui_shared.fg_color)
        name_label.pack(side="left", padx=10, pady=10)

        self.name_entry_input = tk.StringVar()
        add_widget( # This function adds widgets (specifically, entries) and binds necessary stuff automatically
            tk.Entry, name_frame, {'textvariable':self.name_entry_input}, {'text':"Enter the name of the sprite sheet, which is used to display and organize some information."}
        ).pack(side="left", fill="x", expand=True, padx=(0,10), pady=10)

        # Search type

        self.search_types = ["Border", "Spacing", "Preset"] # Options for respective OptionMenu

        search_type_frame = tk.Frame(self.right_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg, height=240)
        search_type_frame.pack(side="top", fill="x")
        search_type_frame.pack_propagate(False) # Prevent automatic resizing, as it kinda looks bad when search type option is changed

        search_type_option_frame = tk.Frame(search_type_frame, bg=gui_shared.bg_color)
        search_type_option_frame.pack(side="top", fill="x")

        search_type_label = tk.Label(search_type_option_frame, text="Search type:", bg=gui_shared.bg_color, fg=gui_shared.fg_color)
        search_type_label.pack(side="left", padx=10, pady=10)
        ToolTip(search_type_label, """
- Border: Searches a border image for boxes that contain poses. When selected, a border layer will be automatically created. Add a valid image, with *perfectly rectangular* pose boxes.

- Spacing: Poses are assumed to be spaced out equally from each other.

- Preset: Use a valid .json file that contains pose data (i.e., one generated with the "Generate Sheet Data..." button) to search for poses in already-known locations.
        """.strip(), False, True) # Not the most optimal string formatting, but this makes my poor, tired brain understand what's going on better

        self.search_type_option = tk.StringVar(value=self.search_types[0])

        # Confusing name, but essentially a frame to hold smaller 'subframes'
        search_type_subframe_container_frame = tk.Frame(search_type_frame, bg=gui_shared.bg_color)
        search_type_subframe_container_frame.pack(side="top", fill="both", expand=True)

        search_border_subframe = tk.Frame(search_type_subframe_container_frame, bg=gui_shared.bg_color) # Subframe for border search type
        search_border_subframe.place(relx=0, rely=0, relwidth=1, relheight=1)

        search_spacing_subframe = tk.Frame(search_type_subframe_container_frame, bg=gui_shared.bg_color) # Subframe for spacing search type
        search_spacing_subframe.place(relx=0, rely=0, relwidth=1, relheight=1)

        search_preset_subframe = tk.Frame(search_type_subframe_container_frame, bg=gui_shared.bg_color) # Subframe for preset search type
        search_preset_subframe.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.search_type_subframes = [search_border_subframe, search_spacing_subframe, search_preset_subframe] # List containing subframes

        self.previous_search_type_option = ""
        self.search_type_option_selected("Border", False) # Automatically select Border as option (TODO: do I need the tk.StringVar(value=...[0])? Does this not do the same thing but better?)

        # Option menu for selecting search type. As much as I would've liked to put all this in gui_shared.add_widget, it just wasn't having it.
        search_type_optionmenu = tk.OptionMenu(search_type_option_frame, self.search_type_option, *self.search_types, command=self.search_type_option_selected)
        # For some reason, can't configure style in the declaration.
        search_type_optionmenu.configure(bg=gui_shared.field_bg, fg=gui_shared.fg_color, activebackground=gui_shared.bg_color, activeforeground=gui_shared.fg_color, anchor="w", justify="left", highlightthickness=1, highlightbackground=gui_shared.secondary_fg, bd=0, relief="flat")
        # Same goes for the dropdown menu.
        search_type_optionmenu["menu"].configure(bg=gui_shared.field_bg, fg=gui_shared.fg_color, activebackground=gui_shared.secondary_bg, activeforeground=gui_shared.fg_color)
        search_type_optionmenu.pack(side="left", padx=(0,10), pady=10, fill="x", expand=True)
        ToolTip(search_type_optionmenu, """
- Border: Searches a border image for boxes that contain poses. When selected, a border layer will be automatically created. Add a valid image with *perfectly rectangular* pose boxes.

- Spacing: Poses are assumed to be spaced out equally from each other.

- Preset: Use a valid .json file that contains pose data (i.e., one generated with the "Generate Sheet Data..." button) to search for poses in already-known locations.
        """.strip(), False, True)

        # Border subframe

        tk.Label(search_border_subframe, text="Border Color:", bg=gui_shared.bg_color, fg=gui_shared.fg_color).grid(padx=5, pady=5, row=1, column=1)

        border_color_input_frame = tk.Frame(search_border_subframe, bg=gui_shared.bg_color)
        border_color_input_frame.grid(row=1, column=2)

        # Swatch showing selected color, as represented by a tiny square with the correct color
        self.border_color_swatch = tk.Canvas(border_color_input_frame, width=20, height=20, bg=self.border_color,
        highlightthickness=1, highlightbackground="black")
        self.border_color_swatch.pack(side="left", padx=5, pady=5)

        self.color_entry_input = tk.StringVar()
        self.color_entry_input.set(self.format_color_string(self.border_color))
        
        color_entry = add_widget(
            tk.Entry, border_color_input_frame, {'width':10, 'textvariable':self.color_entry_input}, {'text':"Type the color that will be interpreted as the border."}
        )
        color_entry.pack(side="left", padx=5, pady=5)
        color_entry.bind("<FocusOut>", self.border_color_entry_input, add="+")

        # This will likely be removed at some point. It's just not that helpful. Maybe, like, a "detect border color" instead? It could search the chosen border image
        pick_border_color_button = tk.Button(search_border_subframe, text="Open Color Picker", command=self.pick_color, bg=gui_shared.button_bg, fg=gui_shared.fg_color)
        pick_border_color_button.grid(padx=5, pady=5, row=1, column=3)
        ToolTip(pick_border_color_button, "Open a color picker and pick the color that will be interpreted as the border.")

        # Spacing subframe

        search_spacing_subframe.grid_anchor("center")
        search_spacing_subframe.grid_columnconfigure(0, weight=1)

        # Rows, columns

        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Grid:").grid(row=0, column=0, padx=10, pady=10, sticky="W")
        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Rows:").grid(row=0, column=1, pady=10, sticky="E")
        
        self.spacing_rows = tk.StringVar()
        self.spacing_rows.set("0")

        add_widget(
            tk.Entry, search_spacing_subframe, {'width':6, 'textvariable':self.spacing_rows}, {'text':"How many rows does the sprite sheet have?"}
        ).grid(row=0, column=2, padx=5, pady=10)

        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Columns:").grid(row=0, column=4, pady=10, sticky="E")

        self.spacing_columns = tk.StringVar()
        self.spacing_columns.set("0")

        add_widget(
            tk.Entry, search_spacing_subframe, {'width':6, 'textvariable':self.spacing_columns}, {'text':"How many columns does the sprite sheet have?"}
        ).grid(row=0, column=5, padx=(5,10), pady=10)

        # Inner/outer padding

        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Padding:").grid(row=1, column=0, padx=10, pady=10, sticky="W")
        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Outer:").grid(row=1, column=1, pady=10, sticky="E")

        self.spacing_outer_padding = tk.StringVar()
        self.spacing_outer_padding.set("0")

        add_widget(
            tk.Entry, search_spacing_subframe, {'width':6, 'textvariable':self.spacing_outer_padding}, {'text':"""How much space between the sprites and the edge of the sprite sheet?\n\n(NOT to be confused with the automatic and custom padding - outer and inner are for the input layer images, automatic and custom are for the output pose images)"""}
        ).grid(row=1, column=2, padx=5, pady=10)

        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="px").grid(row=1, column=3, padx=(0,10), pady=10, sticky="W")
        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Inner:").grid(row=1, column=4, pady=10, sticky="E")

        self.spacing_inner_padding = tk.StringVar()
        self.spacing_inner_padding.set("0")
        add_widget(
            tk.Entry, search_spacing_subframe, {'width':6, 'textvariable':self.spacing_inner_padding}, {'text':"""How much extra padding around each sprite?\n\n(NOT to be confused with the automatic and custom padding - outer and inner are for the input layer images, automatic and custom are for the output pose images)"""}
        ).grid(row=1, column=5, padx=5, pady=10)


        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="px").grid(row=1, column=6, padx=(0,10), pady=10, sticky="W")

        # Separation
        
        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Separation:").grid(row=2, column=0, padx=10, pady=10, sticky="W")
        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="x:").grid(row=2, column=1, pady=10, sticky="E")
        
        self.spacing_x_separation = tk.StringVar()
        self.spacing_x_separation.set("0")

        add_widget(
            tk.Entry, search_spacing_subframe, {'width':6, 'textvariable':self.spacing_x_separation}, {'text':"How much horizontal space between each sprite?"}
        ).grid(row=2, column=2, padx=5, pady=10)

        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="px").grid(row=2, column=3, padx=(0,10), pady=10, sticky="W")
        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="y:").grid(row=2, column=4, pady=10, sticky="E")

        self.spacing_y_separation = tk.StringVar()
        self.spacing_y_separation.set("0")
        add_widget(
            tk.Entry, search_spacing_subframe, {'width':6, 'textvariable':self.spacing_y_separation}, {'text':"How much vertical space between each sprite?"}
        ).grid(row=2, column=5, padx=5, pady=10)

        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="px").grid(row=2, column=6, padx=(0,10), pady=10, sticky="W")

        # Preset Subframe

        search_preset_subframe.grid_columnconfigure(1, weight=1)

        tk.Label(search_preset_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Preset:").grid(row=0, column=0, sticky="W", padx=(10,5), pady=10)

        self.preset_path = tk.StringVar()

        preset_entry = add_widget(
            tk.Entry, search_preset_subframe, {'width':1, 'textvariable':self.preset_path}, {'text':"How much vertical space between each sprite?"}
        )
        preset_entry.grid(row=0, column=1, sticky="EW", pady=10)
        ToolTip(preset_entry, "Enter a path of a preset.  (Preset should be a .json that contains pose data.)")

        self.preset_pose_data = None

        preset_pick_button = tk.Button(search_preset_subframe, bg=gui_shared.button_bg, fg=gui_shared.fg_color, text="📁", command=self.load_preset_json)
        preset_pick_button.grid(row=0, column=2, sticky="E", padx=10, pady=5)
        ToolTip(preset_pick_button, "Choose a preset. (Preset should be a .json that contains pose data.)", False, True)

        self.preset_load_label = tk.Label(search_preset_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="No preset loaded", justify="left")
        self.preset_load_label.grid(row=1, column=0, columnspan=3, sticky="W", padx=10, pady=(0,10))

        # Search options

        search_options_frame = tk.Frame(self.right_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        search_options_frame.pack(side="top", fill="both", expand=True)

        search_options_checkboxes_frame = tk.Frame(search_options_frame, bg=gui_shared.bg_color)
        search_options_checkboxes_frame.pack(side="top", fill="x")

        search_options_checkboxes_frame.grid_anchor("center")

        # Start search in center
        self.start_search_in_center = tk.BooleanVar()
        start_search_in_center_checkbutton = tk.Checkbutton(search_options_checkboxes_frame, text="Start search in center", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, variable=self.start_search_in_center, command=self.set_unsaved_changes)
        start_search_in_center_checkbutton.grid(row=0, column=0, padx=10, pady=5)
        start_search_in_center_checkbutton.select()
        ToolTip(start_search_in_center_checkbutton, """When searching the spritesheet, the program will look at each row starting in the middle of the image, rather than at the edge. It will search outward in one direction before reaching the edge, at which point it will search in the other direction, before moving onto the next row.\n\nRecommended for sprite sheets that group poses in a vertical formation, as it makes the order that pose images are found in much more intuitive. Not recommended if "Search right-to-left" is enabled.""")
        
        # Search right to left
        self.search_right_to_left = tk.BooleanVar()
        search_right_to_left_checkbutton = tk.Checkbutton(search_options_checkboxes_frame, text="Search right-to-left", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, variable=self.search_right_to_left, command=self.set_unsaved_changes)
        search_right_to_left_checkbutton.grid(row=0, column=1, padx=10, pady=5)
        ToolTip(search_right_to_left_checkbutton, """Search the spritesheet from right-to-left, instead of from left-to-right.\n\nRecommended if "Start search in center" is disabled, as most characters face right by default, and most sprite sheets show the rightmost sprites on the right side of the sheet, so the generated data will use the right-facing poses as the defaults. Not recommended otherwise.""")

        # Detect identical images
        self.detect_identical_images = tk.BooleanVar()
        detect_identical_images_checkbutton = tk.Checkbutton(search_options_checkboxes_frame, text="Detect identical images", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, variable=self.detect_identical_images, command=self.set_unsaved_changes)
        detect_identical_images_checkbutton.grid(row=1, column=0, padx=10, pady=(10,5))
        detect_identical_images_checkbutton.select()
        ToolTip(detect_identical_images_checkbutton, """Check if poses use already-found pose images, so they can share the same pose image.\n\n(Highly recommended - this is kinda the whole point)""")

        # When rotated is selected, flip_v is redundant and therefore disabled for clarity
        def check_flip_v_allowed():
            if self.detect_rotated_images.get():
                self.detect_flip_v_images.set(False)
                detect_flip_v_images_checkbutton.configure(state='disabled')
            else:
                detect_flip_v_images_checkbutton.configure(state='normal')

        # Detect rotated images
        self.detect_rotated_images = tk.BooleanVar()
        detect_rotated_images_checkbutton = tk.Checkbutton(search_options_checkboxes_frame, text="Detect rotated images", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, variable=self.detect_rotated_images, command=lambda: [check_flip_v_allowed(), self.set_unsaved_changes()])
        detect_rotated_images_checkbutton.grid(row=1, column=1, padx=10, pady=(10,5))
        detect_rotated_images_checkbutton.select()
        ToolTip(detect_rotated_images_checkbutton, "Check if poses use rotated versions of already-found pose images.")

        # Detect horizontally mirrored images
        self.detect_flip_h_images = tk.BooleanVar()
        detect_flip_h_images_checkbutton = tk.Checkbutton(search_options_checkboxes_frame, text="Detect horizontally mirrored images", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, variable=self.detect_flip_h_images, command=lambda: [check_flip_v_allowed(), self.set_unsaved_changes()])
        detect_flip_h_images_checkbutton.grid(row=2, column=0, columnspan=2, padx=10, pady=5)
        detect_flip_h_images_checkbutton.select()
        ToolTip(detect_flip_h_images_checkbutton, "Check if poses use horizontally-flipped versions of already-found pose images.")
        
        # Detect vertically mirrored images
        self.detect_flip_v_images = tk.BooleanVar()
        detect_flip_v_images_checkbutton = tk.Checkbutton(search_options_checkboxes_frame, text="Detect vertically mirrored images", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, variable=self.detect_flip_v_images, state='disabled', command=self.set_unsaved_changes)
        detect_flip_v_images_checkbutton.grid(row=3, column=0, columnspan=2, padx=10, pady=(5,10))
        ToolTip(detect_flip_v_images_checkbutton, """Check if poses use vertically-flipped versions of already-found pose images.\n\n(Automatically disabled when using "detect rotated" to avoid redundancy; a horizontally-flipped, 180-degrees-rotated image is identical to a vertically-flipped image, so just use "detect rotated" with "detect h-mirrored" instead.)""")

        # Generation options

        # Generate empty poses
        self.generate_empty_poses = tk.BooleanVar()
        generate_empty_poses_checkbutton = tk.Checkbutton(search_options_checkboxes_frame, text="Generate empty poses", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, variable=self.generate_empty_poses, command=self.set_unsaved_changes)
        generate_empty_poses_checkbutton.grid(row=4, column=0, columnspan=2, padx=10, pady=(5,10))
        ToolTip(generate_empty_poses_checkbutton, "Determine whether pose data will be created for pose boxes that are completely empty.")

        self.padding_types = ["Show only always-visible pixels", "Show all theoretically-visible pixels", "None"] # Options for respective OptionMenu

        padding_label = tk.Label(search_options_frame, text="Automatic padding type:", bg=gui_shared.bg_color, fg=gui_shared.fg_color)
        padding_label.pack(side="top", padx=10, pady=10)

        self.automatic_padding_type_option = tk.StringVar(value=self.padding_types[0])
        
        padding_type_optionmenu = tk.OptionMenu(search_options_frame, self.automatic_padding_type_option, *self.padding_types)
        padding_type_optionmenu.configure(bg=gui_shared.field_bg, fg=gui_shared.fg_color, activebackground=gui_shared.bg_color, activeforeground=gui_shared.fg_color, width=28, anchor="w", justify="left", highlightthickness=1, highlightbackground=gui_shared.secondary_fg, bd=0, relief="flat")
        padding_type_optionmenu["menu"].configure(bg=gui_shared.field_bg, fg=gui_shared.fg_color, activebackground=gui_shared.secondary_bg, activeforeground=gui_shared.fg_color)
        padding_type_optionmenu.pack(side="top", padx=10, pady=(0,10))
        ToolTip(padding_type_optionmenu, """
- Show only always-visible pixels: Padding for pose images will increase to show how much space is visible in all instances of that pose image. (Recommended)

- Show all theoretically-visible pixels: Same as above, but padding also contains space that is not visible in some pose boxes.

- None: No extra automatic padding is applied. (Recommended if using the "Custom padding" option.)
        """.strip())

        custom_padding_frame = tk.Frame(search_options_frame, bg=gui_shared.bg_color)
        custom_padding_frame.pack(side="top")

        tk.Label(custom_padding_frame, text="Custom padding amount:", bg=gui_shared.bg_color, fg=gui_shared.fg_color).pack(side="left", padx=(10,5), pady=10)

        # Despite needing to store an int, allow string input and just complain if that's submitted for generation. Not sure if this is the best way to do it,
        # and it DID seem to work with a tk.IntVar(), but this is fine...
        self.custom_padding_amount = tk.StringVar()
        self.custom_padding_amount.set("0")
        add_widget(
            tk.Entry, custom_padding_frame, {'width':6, 'textvariable':self.custom_padding_amount}, {'text':"""Enter a custom amount of padding to apply to each pose image. If used alongside automatic padding, this will add the automatic and custom padding together.\n\n(Negative values are allowed, and will instead subtract from automatic padding without cutting off any of the pose images.)"""}
        ).pack(side="left", pady=10)

        generate_frame = tk.Frame(self.right_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        generate_frame.pack(side="bottom", fill="x")

        generate_options_frame = tk.Frame(generate_frame, bg=gui_shared.bg_color)
        generate_options_frame.pack(side="top", fill="x")

        tk.Label(generate_options_frame, text="Output folder path:", bg=gui_shared.bg_color, fg=gui_shared.fg_color).pack(side="left", padx=(10,5), pady=10)

        # Output folder selection

        self.output_folder_path = tk.StringVar()
        output_folder_entry = add_widget(
            tk.Entry, generate_options_frame, {'textvariable':self.output_folder_path, 'width':1}, {'text':"""Enter the path to the folder where the pose images and .json data will be output.\n\n(It's recommended that you choose a new, EMPTY folder! Choosing an existing one will clutter up your files at best, and overwrite existing data at worst. That said, if you WANT to overwrite existing data, go for it.)"""}
        )
        output_folder_entry.pack(side="left", fill="x", expand=True, pady=10)

        def select_output_folder_path():
            path = filedialog.askdirectory(title="Select an output folder (preferably empty)")
            if path and ((not os.listdir(path)) or gui_shared.warn_overwrite()):
                self.output_folder_path.set(path)

        output_folder_button = tk.Button(generate_options_frame, text="📁", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=select_output_folder_path)
        output_folder_button.pack(side="left", padx=10, pady=10)
        ToolTip(output_folder_button, """Open a file dialog and select the folder where the pose images and .json data will be output.\n\n(It's recommended that you choose a new, EMPTY folder! Choosing an existing one will clutter up your files at best, and overwrite existing data at worst. That said, if you WANT to overwrite existing data, go for it.)""")

        # Generate buttons/displays

        generate_container_frame = tk.Frame(generate_frame, bg=gui_shared.bg_color)
        generate_container_frame.pack(side="top", fill="x")

        generate_buttons_frame = tk.Frame(generate_container_frame, bg=gui_shared.bg_color)
        generate_buttons_frame.pack(side="left")

        # Generate button
        self.generate_button = tk.Button(generate_buttons_frame, text="Generate Sheet Data...", command=self.generate_button_pressed, bg=gui_shared.button_bg, fg=gui_shared.fg_color)
        self.generate_button.pack(side="top", padx=10, pady=10)
        ToolTip(self.generate_button, "Search the sprite sheet according to the selected search options. Then, generate sprite sheet data and pose images.\n\n(Depending on how many layers the sheet has, this may take a while.)", True)

        # Cancel button
        self.cancel_button = tk.Button(generate_buttons_frame, text="Cancel", command=self.cancel_generate, fg=gui_shared.danger_fg, bg=gui_shared.button_bg, state="disabled")
        self.cancel_button.pack(side="top", padx=10, pady=(0,10), fill="x")
        ToolTip(self.cancel_button, "Cancel search and/or generation", True)
        
        generate_progress_frame = tk.Frame(generate_container_frame, bg=gui_shared.bg_color)
        generate_progress_frame.pack(side="left", fill="x", expand=True)

        # Label contains first line if there are multiple lines. Exists at all times, despite only *really* needing one textobx so that widget positions are consistent.
        self.progress_header_label = tk.Label(generate_progress_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color)
        self.progress_header_label.pack(side="top", padx=(0,10), pady=(10,0), fill="x", expand=True)

        # Label contains second line if there are multiple lines, and ONLY line if there's ONLY ONE line. Could definitely make this system less rigid I think
        self.progress_info_label = tk.Label(generate_progress_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color)
        self.progress_info_label.pack(side="top", padx=(0,10), pady=(0,5), fill="x", expand=True)

        # Progress bar        
        self.progress_bar = ttk.Progressbar(generate_progress_frame, orient="horizontal", maximum=100)
        self.progress_bar.pack(padx=(0,10), pady=(0,10), side="top", fill="x", expand=True)

        self.bind_all("<Button-1>", gui_shared.on_global_click, add="+") # Bind entry color change to all widgets. This is important I swear

        if load_path: # If a path was passed as a parameter, load it 
            self.import_layerselect_json(load_path)

    # Controls layer menu scrolling
    def _on_left_frame_mousewheel(self, event):
        delta = -1 * (event.delta // 120)
        self.layer_canvas.yview_scroll(delta, "units")

    # Open color picker menu, select color
    def pick_color(self):
        color = colorchooser.askcolor(title="Pick Background Color")[1]
        if color:
            self.update_border_color(color)

    # Change the color, notify user if it's invalid
    def update_border_color(self, color = None):
        try:
            color = self.format_color_string(color) # Get formatted string

            self.border_color_swatch.configure(bg=color) # Change swatch color
            self.color_entry_input.set(color) # Set color entry
            self.border_color = color # Set border color

            self.set_unsaved_changes(True)
        except:
            messagebox.showerror("Error", "Enter a valid color") # Inform user that entered color is invalid

    # Update the border color
    def border_color_entry_input(self, _event):
        self.update_border_color(self.color_entry_input.get())
    
    # Ensure that color strings are formatted with a # character in front
    def format_color_string(self, color):
        # Definitely stupid to remove a character to just re-add it in the next line, but this is a quick and easy way to make sure input WITHOUT the # char
        # is formatted exactly the same. The lstrip does not effect strings that DON'T have that line, so they're on an even playing field by the time the #
        # is added back.
        color = color.lstrip("#")
        color = "#" + color
        
        return color

    # Look at all stored layer data, and get the size of the first image found
    def force_get_image_size(self):
        for layer in self.layer_data:
            path = layer.get("search_image_path", layer.get("source_image_path")) # if no search img, get source img. if neither, it's None

            if path and gui_shared.check_image_valid(path)[0]: # If there's a path, and that path contains a valid image:
                with Image.open(path) as image:
                    self.image_size = image.size
                    return

    # Add a blank layer card
    def add_blank_layer(self, add_to_top = True):
        blank_layer = {
            "name": None,
            "search_image_path": None,
            "source_image_path": None,
            "is_border": False,
            "is_cosmetic_only": False,
            "export_layer_images": False,
            "thumbnail": None
        }
        
        if add_to_top:
            self.layer_data.insert(0, blank_layer) # Add to top
            self.redraw_all_layer_cards() # Redraw all, since all layer numbers will be changed
        else:
            self.layer_data.append(blank_layer) # Add to bottom
            self.redraw_layer_card(len(self.layer_data) - 1) # Redraw only bottom card

        self.set_unsaved_changes(True)

        # self.redraw_all_layer_cards()

    # Add multiple layer cards. A bit misleading - it works for adding from images, but mostly exists for loading existing layer data.
    def add_image_layers(self, data = None, add_to_top = True):
        if not data: # If no existing data was passed, ask user for image paths and format as if it were normal layer data
            paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])

            data = []
            for path in paths:
                data.append({"name": os.path.splitext(os.path.basename(path))[0], "search_image_path": path})

        for d in (reversed(data) if add_to_top else data):
            # Format existing layer data
            name = d.get("name")
            search_image_path = d.get("search_image_path")
            source_image_path = d.get("source_image_path")
            is_border = d.get("is_border", False)
            is_cosmetic_only = d.get("is_cosmetic_only", False)
            export_layer_images = d.get("export_layer_images", False)
            
            new_layer = { # Create specific layer data
                "name": name,
                "search_image_path": search_image_path,
                "source_image_path": source_image_path,
                "is_border": is_border,
                "is_cosmetic_only": is_cosmetic_only,
                "export_layer_images": export_layer_images,
            }

            if add_to_top: # Add to layer data list
                self.layer_data.insert(0, new_layer)
            else:
                self.layer_data.append(new_layer)
        
        if len(data): # i.e. if any layers exist
            self.set_unsaved_changes(True)
            # if add_to_top: self.redraw_all_layer_cards()
            self.redraw_all_layer_cards()
            self.set_preview_button(True)

    # Create a thumbnail for a layer card from the search image.
    # (Cannot simply return the image, as nice as that would be; it goes out of scope and ceases to exist, so it instead needs to be stored)
    def create_layer_thumbnail(self, layer_index):
        try:
            if self.layer_data[layer_index].get("search_image_path") and gui_shared.check_image_valid(self.layer_data[layer_index].get("search_image_path"))[0]: # TODO make better check
                with Image.open(self.layer_data[layer_index].get("search_image_path")) as image:
                    thumbnail = image.copy()
                thumbnail.thumbnail((64,64)) # Image.Resampling.NEAREST, maybe? idk

                self.layer_data[layer_index].update({"thumbnail":ImageTk.PhotoImage(thumbnail)})
                return
        except Exception as e:
            pass # exception is likely that image does not exist

        self.layer_data[layer_index].update({"thumbnail":None})

    # Change the search type, and make other changes if necessary.
    def search_type_option_selected(self, selected_option, set_unsaved_changes = True):
        self.search_type_subframes[self.search_types.index(selected_option)].lift() # Raise subframe to be on top

        # if selected_option == "Border":
        if selected_option == "Border" and self.previous_search_type_option != "Border":
            self.add_border_layer() # TODO This should ONLY run if something has actually changed
        # else:
        elif selected_option != "Border" and self.previous_search_type_option == "Border":
            border_index = next((i for i, layer in enumerate(self.layer_data) if layer["is_border"]), None)
            if border_index != None: self.delete_layer(border_index)
            
        if set_unsaved_changes and selected_option != self.previous_search_type_option: # Hackey solution to making this not run upon creating new menu.
            self.set_unsaved_changes(True)
        
        self.previous_search_type_option = selected_option # To ensure stuff isn't done multiple times if the current choice is selected a second time in a row

    # Add a border layer. (In the future, the border system needs to be more modular; a checkbox like the is_cosmetic_only on would work well, but would need better integration with the border subframe)
    def add_border_layer(self):
        self.layer_data.append({
            "name": "border",
            "is_border": True,
            "is_cosmetic_only": True, # TODO changed. i imagine this is how it should be, but test anyway. it didnt cause issues when False
            "search_image_path": None,
            "source_image_path": None,
            "thumbnail": None
        })
        
        self.redraw_layer_card(len(self.layer_data) - 1) # Redraw only bottom card
        # TODO scroll the frame all the way down?

    # Load a preset .json containing pose data.
    def load_preset_json(self):
        ok = True
        if self.preset_pose_data:
            ok = messagebox.askokcancel("Warning!", "Other pose data is already loaded. If you load another file, the current pose data will be replaced.")
        if ok:
            path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("Json File", "*.json")])
            if path:
                try:
                    self.preset_path.set(path)
                    with open(path) as preset_json:
                        preset_data = json.load(preset_json)
                    self.set_preset_pose_data(preset_data["pose_data"])
                except json.JSONDecodeError as e:
                    pass # print exception: json invalid
                # other exceptions?
    
    # Set the preset pose data, and update the relevant label
    def set_preset_pose_data(self, preset_pose_data):
        self.preset_pose_data = preset_pose_data
        self.preset_load_label.config(text=f"Pose data loaded as preset.\nPoses: {len(self.preset_pose_data)}")

    # Move a layer up or down
    def move_layer(self, index, direction):
        new_index = index + direction
        
        if 0 <= new_index < len(self.layer_data):
            
            self.layer_data[index], self.layer_data[new_index] = self.layer_data[new_index], self.layer_data[index]

            self.redraw_layer_card(index)
            self.redraw_layer_card(new_index)

            self.set_unsaved_changes(True)
            self.set_preview_button(True)

    # Delete a layer
    def delete_layer(self, layer_index):
        had_search_image = self.layer_data[layer_index].get("search_image_path") != None

        del self.layer_data[layer_index]
        self.set_unsaved_changes(True)

        # could theoretically just do all layer cards *after* the deleted index, but also .redraw_all_layer_cards() has the necessary delete functionality
        self.redraw_all_layer_cards()

        if had_search_image: self.set_preview_button(True)

    # Redraw a layer card. (Complex enough that layer cards ought to be their own class. Will do that eventually)
    def redraw_layer_card(self, layer_index):
        # If card frame doesn't exist, create a new one. If it does, might as well use the existing one so we don't have to worry about re-ordering everything.
        card_frame : tk.Frame = None
        if layer_index >= len(self.scrollable_frame.winfo_children()):
            card_frame = tk.Frame(self.scrollable_frame, bg=gui_shared.secondary_bg, highlightthickness=1, highlightbackground=gui_shared.secondary_fg, pady=0)
            card_frame.pack(side="top", fill="x", expand=True, padx=10)
        else:
            card_frame = self.scrollable_frame.winfo_children()[layer_index]
            card_frame.configure(width=0)
            card_frame.pack_propagate(True) # Prepare to get new automatic size

            # Destroy all existing widgets.
            for widget in card_frame.winfo_children():
                widget.destroy()
        
        # Set pady, which is different depending on if the layer card is on the very top
        card_frame.pack_configure(pady=((10 if (layer_index == 0) else 0), 10))

        # Get this layer's data, for convenience
        data : dict = self.layer_data[layer_index]

        # Lots of things are formatted differently based on chosen settings 
        is_border = data.get("is_border", False)
        is_cosmetic_only = data.get("is_cosmetic_only", False)

        # Contains everything but the buttons on the right
        content_frame = tk.Frame(card_frame, bg=gui_shared.secondary_bg)
        content_frame.pack(side="left", fill="both", expand=True)

        # Contains thumbnail, layer num, and entries
        content_top_frame = tk.Frame(content_frame, bg=gui_shared.secondary_bg)
        content_top_frame.pack(side="top", fill="both", expand=True)

        # Contains thumbnail and layer num
        content_left_frame = tk.Frame(content_top_frame, bg=gui_shared.secondary_bg, highlightthickness=1, highlightbackground=gui_shared.secondary_fg, width=80)
        content_left_frame.pack(side="left", fill="y")

        tk.Label(content_left_frame, text=f"Layer {layer_index+1}", bg=gui_shared.secondary_bg, fg=gui_shared.fg_color).pack(side="top", fill="x", padx=10, pady=(10,0))

        if data.get("search_image_path") and not data.get("thumbnail"): # If a thumbnail could exist and does not, create it
            self.create_layer_thumbnail(layer_index)

        # Place thumbnail. (I eventually want a checkerboard background for better visibility, but I don't know if it would actually help since the imgs are so small)
        tk.Label(content_left_frame, image=data.get("thumbnail"), bg=gui_shared.field_bg).pack(side="top", fill="both", expand=True, padx=10, pady=10)

        # Contains the entries, plus their respective buttons and labels
        content_right_frame = tk.Frame(content_top_frame, bg=gui_shared.secondary_bg, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        content_right_frame.pack(side="right", fill="both", expand=True)

        # Name input

        # Separate frame for name label & entry, for formatting's sake
        name_frame = tk.Frame(content_right_frame, bg=gui_shared.secondary_bg)
        name_frame.pack(side="top", fill="x", padx=10, pady=(10,0))

        tk.Label(name_frame, text=("Border" if is_border else "Name:"), bg=gui_shared.secondary_bg, fg=gui_shared.fg_color).pack(side="left", padx=(0,5))

        if not is_border:
            # Uses custom function that styles widget automatically, and also adds some binds that are tedious to do manually
            name_entry = add_widget(tk.Entry, name_frame, {'width':1}, {'text':"Enter this layer's name."})
            name_entry.pack(side="left", fill="x", expand=True)
            
            if data.get("name"): # If a name already exists, use it
                name_entry.insert(0, data.get("name"))

            def save_name(e, entry=data, entry_widget=name_entry): # Uses parameters rather than relying on normal variables, which usually only apply to latest layer
                entry.update({"name":entry_widget.get()})
                self.set_unsaved_changes(True)

            # It might be easier to use, say, a tk.StringVar(), but this feels better because layers can be created and destroyed dynamically & I don't wanna worry
            # about updating a bunch of lists of variables and stuff
            name_entry.bind("<FocusOut>", save_name, add="+")

        # Search image stuff

        # Separate frame for search image label, entry, and button
        search_frame = tk.Frame(content_right_frame, bg=gui_shared.secondary_bg)
        search_frame.pack(side="top", fill="x", padx=10, pady=((0 if is_border else 10), (10 if is_cosmetic_only else 0)))

        tk.Label(
            search_frame, text=("Image:" if is_border or is_cosmetic_only else "Search img:"), bg=gui_shared.secondary_bg, fg=gui_shared.fg_color
        ).pack(side="left", padx=(0,5))

        search_entry = add_widget(tk.Entry, search_frame, {'width':1}, {'text':"Enter the path to this layer's image, which will be searched for poses."})
        search_entry.pack(side="left", fill="x", expand=True)
        
        if data.get("search_image_path"):
            search_entry.insert(0, data.get("search_image_path"))

        # Save the search image in self.layer_data[layer_index]
        def save_search_image(e = None, entry=data, entry_widget=search_entry, i=layer_index):
            new_image_path = entry_widget.get()

            entry.update({"search_image_path":new_image_path})
                
            self.create_layer_thumbnail(i) # Force a thumbnail update
            
            self.redraw_layer_card(i) # Only need to redraw THIS card

            self.set_preview_button(True)
            self.set_unsaved_changes(True)

        search_entry.bind("<FocusOut>", save_search_image, add="+")

        # Open a file dialog and pick the search image
        def pick_search_image(entry=data, entry_widget=search_entry):
            new_path = filedialog.askopenfilename(title="Select an image for this layer", filetypes=[("Image File", "*.png;*.jpg;*.jpeg")])
            if new_path and gui_shared.warn_image_valid(new_path):
                if entry_widget.get():
                    # Ran into weird error relating to this line, so into an if statement it goes. No idea if this helps
                    entry_widget.delete(0, tk.END)
                
                entry_widget.insert(0, new_path)
                save_search_image(entry=entry, entry_widget=entry_widget)

        search_button = tk.Button(search_frame, text="📁", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=pick_search_image)
        search_button.pack(side="left", padx=(10,0))
        ToolTip(search_button, "Open a file dialog and select this layer's image, which will be searched for poses.")
        
        # Source image stuff
        if not is_border and not is_cosmetic_only: # TODO: make source image disabled if search image entry is empty? idk
            source_frame = tk.Frame(content_right_frame, bg=gui_shared.secondary_bg)
            source_frame.pack(side="top", fill="x", padx=10, pady=(0,10))

            tk.Label(source_frame, text="Source img:", bg=gui_shared.secondary_bg, fg=gui_shared.fg_color).pack(side="left", padx=(0,5))

            source_entry = add_widget(tk.Entry, source_frame, {'width':1}, {'text':"""(OPTIONAL!) The search image is used to find identical copies, but the source image is used for the actual image output. If no source image is selected, the search image will be used instead.\n\n(Just leave this empty if you're not sure.)"""})
            source_entry.pack(side="left", fill="x", expand=True)
            
            if data.get("source_image_path"):
                source_entry.insert(0, data.get("source_image_path"))

            # Save the search image in self.layer_data[layer_index]
            def save_source_image(e = None, entry=data, entry_widget=source_entry):
                new_image_path = entry_widget.get()
                entry.update({"source_image_path":new_image_path})
                self.set_unsaved_changes(True)

            source_entry.bind("<FocusOut>", save_source_image, add="+")

            # Open a file dialog and pick the search image
            def pick_source_image(entry=data, entry_widget=source_entry):
                new_path = filedialog.askopenfilename(title="Select an image for this layer", filetypes=[("Image File", "*.png;*.jpg;*.jpeg")])
                if new_path and gui_shared.warn_image_valid(new_path):
                    if entry_widget.get():
                        entry_widget.delete(0, tk.END)
                    entry_widget.insert(0, new_path)
                    save_source_image(entry=entry, entry_widget=entry_widget)
            
            source_button = tk.Button(source_frame, text="📁", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=pick_source_image)
            source_button.pack(side="left", padx=(10,0))
            ToolTip(source_button, "(OPTIONAL!) The search image is used to find identical copies, but the source image is used for the actual image output. If no source image is selected, the search image will be used instead.\n\n(Just leave this alone if you're not sure.)")

        # Layer control buttons

        right_frame = tk.Frame(card_frame, bg=gui_shared.secondary_bg, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        right_frame.pack(side="right", fill="y")

        if not is_border:
            x_button = tk.Button(right_frame, width=2, text="X", fg=gui_shared.danger_fg, command=lambda idx=layer_index: self.delete_layer(idx), bg=gui_shared.button_bg)
            x_button.pack(side="top", padx=10, pady=(10,0))
            ToolTip(x_button, f"Delete layer {layer_index+1}")

        down_button = tk.Button(right_frame, width=2, text="↓", command=lambda idx=layer_index: self.move_layer(idx, 1), bg=gui_shared.button_bg, fg=gui_shared.fg_color)
        down_button.pack(side="bottom", padx=10, pady=(0,10))
        ToolTip(down_button, "Reorder " + ("border" if is_border else f"layer {layer_index+1}") + " downwards")

        up_button = tk.Button(right_frame, width=2, text="↑", command=lambda idx=layer_index: self.move_layer(idx, -1), bg=gui_shared.button_bg, fg=gui_shared.fg_color)
        up_button.pack(side="bottom", padx=10, pady=(10,0))
        ToolTip(up_button, "Reorder " + ("border" if is_border else f"layer {layer_index+1}") + " upwards")

        # Footer containing various options
        if not is_border:
            footer = tk.Frame(content_frame, bg=gui_shared.secondary_bg, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
            footer.pack(side="bottom", fill="both")

            cosmetic_checkbutton = tk.Checkbutton(footer, text="Cosmetic only", bg=gui_shared.secondary_bg, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False)
            cosmetic_checkbutton.pack(side="left", padx=10, pady=5)
            if is_cosmetic_only: cosmetic_checkbutton.select()
            ToolTip(cosmetic_checkbutton, "If selected, this layer will not be searched for pose images. Instead, the provided image will be exported alongside the pose images.")

            # Toggle cosmetic bool
            def save_cosmetic_check(entry=data, cosmetic=is_cosmetic_only, i=layer_index):
                entry.update({"is_cosmetic_only": not cosmetic})
                self.redraw_layer_card(i)
                self.set_unsaved_changes(True)
                
            cosmetic_checkbutton.configure(command=save_cosmetic_check)

            if is_cosmetic_only:
                data.update({"export_layer_images":True})
                
            export_checkbutton = tk.Checkbutton(footer, text="Export copies", bg=gui_shared.secondary_bg, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, state="disabled" if is_cosmetic_only else "normal")
            export_checkbutton.pack(side="left", padx=(0,10), pady=5)
            if data.get("export_layer_images"): export_checkbutton.select()
            ToolTip(export_checkbutton, "If selected, copies of the search and source image will be provided in addition to pose images.")

            # Toggle export check
            def save_export_check(entry=data):
                entry.update({"export_layer_images": entry.get("export_layer_images") != True})
                self.set_unsaved_changes(True)
                
            export_checkbutton.configure(command=save_export_check)
        else:
            data["is_cosmetic_only"] = True
            data["export_layer_images"] = True

        self.update_layer_card_width(layer_index)

        gui_shared.bind_event_to_all_children(card_frame, "<MouseWheel>", self._on_left_frame_mousewheel) # Bind scrolling
        gui_shared.bind_event_to_all_children(card_frame, "<Button-1>", gui_shared.on_global_click) # Bind entry color change

    # Redraw every layer card
    def redraw_all_layer_cards(self):
        # TODO store scroll location
        
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for i in range(len(self.layer_data)):
            self.redraw_layer_card(i)
        
        # TODO scroll back to that location

    # Update a specified layer card's width
    def update_layer_card_width(self, layer_index):
        if layer_index >= len(self.scrollable_frame.winfo_children()):
            return # idk PROBABLY raise exception? idk!!!
        else:
            # get card
            card_frame : tk.Frame = self.scrollable_frame.winfo_children()[layer_index]

            # reset card size to what it wants to be automatically
            card_frame.configure(width=0)
            card_frame.pack_propagate(True)
            card_frame.update_idletasks()
            
            card_height = card_frame.winfo_height() # get automatically-sized height
            card_frame.pack_propagate(False) # stop using automatic size
            card_frame.configure(width=self.layer_canvas_frame.winfo_width() - 18, height=card_height) # need to calibrate width such that padding and scrollbar is kept in mind. COULD definitely do something like the height, and only .pack() stuff with card_frame as master at the very end? but you'd need to do smth like, "save the width, then after everything's packed you can save the height and THEN turn off pack_propagate"

    # Change the color of the 'update preview' button
    def set_preview_button(self, can_update = True):
        self.update_preview_button.configure(
            bg=(gui_shared.warning_bg if can_update else gui_shared.button_bg), fg=(gui_shared.warning_fg if can_update else gui_shared.fg_color)
        )

    # Get a new preview image
    def update_preview_image(self):
        self.set_preview_button(False) # Change button color back to normal

        for layer in self.layer_data: # Verify that images are valid
            if ((layer.get("search_image_path") and not gui_shared.check_image_valid(layer.get("search_image_path"))[0])
                or (layer.get("source_image_path") and not gui_shared.check_image_valid(layer.get("source_image_path"))[0])):
                messagebox.showwarning("Warning!", "At least one image is invalid. Check that they exist and are the correct filetype.")
                return

        self.force_get_image_size() # Get the image size, even if one already exists, as the size may have changed.

        if not (gui_shared.warn_image_sizes(["Search image", "Source image"], # If the images are different sizes, warn the user and do not continue
            [
                [layer.get("search_image_path") for layer in self.layer_data],
                [layer.get("source_image_path") for layer in self.layer_data]
            ]
        )): return

        if self.image_size != None: # If any images exist, setup new preview image
            self.preview_image = Image.new("RGBA", self.image_size, ImageColor.getrgb(gui_shared.field_bg))
        else: # If no images exist, self.image_size will be None
            self.preview_viewportcanvas.set_image(None) # clear ViewportCanvas image, since no images exist
            return

        for layer in reversed(self.layer_data): # Start at the bottom layer, and add each search image to the preview
            if layer.get("search_image_path") and gui_shared.check_image_valid(layer.get("search_image_path"))[0]: # TODO make better check
                with Image.open(layer["search_image_path"]) as image: # TODO at some point, could have an alt version for source images? maybe a button on preview footer chooses which to look at
                    self.preview_image.alpha_composite(image)
        
        self.preview_viewportcanvas.set_image(self.preview_image) # Set ViewportCanvas image

    # Format the selected data for use in exports/generation
    def format_layer_json(self, json_type = "layerselect_save_json"):
        name = self.name_entry_input.get() or "unnamed_sprite_sheet"

        header = {
            "name": name,
            "consistxels_version": consistxels_version,
            "type": json_type,
            # "width": None,
            # "height": None # Not sure if we NEED the size here? I dunno
        }

        search_data = {
            "start_search_in_center": self.start_search_in_center.get(),
            "search_right_to_left": self.search_right_to_left.get(),
            "detect_identical_images": self.detect_identical_images.get(),
            "detect_rotated_images": self.detect_rotated_images.get(),
            "detect_flip_h_images": self.detect_flip_h_images.get(),
            "detect_flip_v_images": self.detect_flip_v_images.get()
        }

        search_type = self.search_type_option.get()

        search_type_data = {
            "search_type": search_type
        }

        if search_type == "Border":
            search_type_data.update({
                "border_color": self.border_color,
                "spacing_rows": None,
                "spacing_columns": None,
                "spacing_outer_padding": None,
                "spacing_inner_padding": None,
                "spacing_x_separation": None,
                "spacing_y_separation": None
            })
        elif search_type == "Spacing":
            # it MIGHT be a good idea to try/except here. since ALL of the export funcs use this. idk. might be better
            search_type_data.update({
                "border_color": None,
                "spacing_rows": int(self.spacing_rows.get()),
                "spacing_columns": int(self.spacing_columns.get()),
                "spacing_outer_padding": int(self.spacing_outer_padding.get()),
                "spacing_inner_padding": int(self.spacing_inner_padding.get()),
                "spacing_x_separation": int(self.spacing_x_separation.get()),
                "spacing_y_separation": int(self.spacing_y_separation.get())
            })
        
        pose_data = self.preset_pose_data
        
        generation_data = {
            "automatic_padding_type": self.automatic_padding_type_option.get(),
            "custom_padding_amount": int(self.custom_padding_amount.get()),
            "generate_empty_poses": self.generate_empty_poses.get()
        }

        layer_data = [] # Create new layer data, since self.layer_data stores the thumbnails too
        for i, layer in enumerate(self.layer_data):
            search_image_path = layer.get("search_image_path")
            if search_image_path and json_type == "layerselect_save_folder":
                search_image_path = ( # Create the image name. It's a bit horrendous :(
                    f"""layer{i + 1}_{(f'''{(
                        'border' if layer.get('is_border') else (
                        f"{layer.get('name', 'unnamed_layer')}{(
                            '_cosmetic_layer' if layer.get('is_cosmetic_only') else ('_search' if layer.get('source_image_path') else '')
                        )}")
                    )}''')}_image.png"""
                )

            elif search_image_path == "": search_image_path = None

            source_image_path = layer.get("source_image_path")
            if source_image_path and json_type == "layerselect_save_folder": source_image_path = f"layer{i + 1}_{layer('name', 'unnamed_layer')}_source_image.png"
            elif source_image_path == "": source_image_path = None

            layer_data.append({
                "name": layer.get("name"),
                "search_image_path": search_image_path,
                "source_image_path": source_image_path,
                "is_border": layer.get("is_border", False),
                "is_cosmetic_only": layer.get("is_cosmetic_only", False),
                "export_layer_images": layer.get("export_layer_images", False)
            })
        
        formatted_data = {
            "header": header,
            "search_data": search_data,
            "search_type_data": search_type_data,
            "generation_data": generation_data,
            "layer_data": layer_data
        }

        if pose_data:
            formatted_data.update({"pose_data": pose_data}) # Only add the pose_data if it actually exists

        if json_type == "layerselect_save_json": # Only save the output folder path if this is a local save, not meant for transferring
            output_folder_path = self.output_folder_path.get()
            if output_folder_path and output_folder_path != "":
                formatted_data.update({"output_folder_path": output_folder_path})

        return formatted_data

    # Export a .json and all layer images
    def export_layerselect_all(self):
        try:
            formatted_data = self.format_layer_json("layerselect_save_folder")
        except ValueError:
            messagebox.showwarning("Warning!", "Please ensure all text input boxes are filled out correctly.\nIf a number is required, don't enter anything else.")
            return
        except Exception as e:
            messagebox.showerror("Error", e)
            return

        path = filedialog.askdirectory(title="Select an output folder (preferably empty)") # Get save output path (different than output folder path; that's just for generation)
        if path and ((not os.listdir(path)) or gui_shared.warn_overwrite()): # Make sure there's a path, and warn user if it's not empty
            layer_data = formatted_data["layer_data"]
            for i in range(len(layer_data)):
                if self.layer_data[i].get("search_image_path") and gui_shared.check_image_valid(self.layer_data[i].get("search_image_path"))[0]: # TODO make better check
                    with Image.open(self.layer_data[i].get("search_image_path")) as search_image:
                        search_image.save(os.path.join(path, layer_data[i]["search_image_path"])) # Save search image
                
                if self.layer_data[i].get("source_image_path") and gui_shared.check_image_valid(self.layer_data[i].get("source_image_path"))[0]: #TODO make better check
                    with Image.open(self.layer_data[i].get("source_image_path")) as source_image:
                        source_image.save(os.path.join(path, layer_data[i]["source_image_path"])) # Save source image
            
            json_path = os.path.join(path, f"consistxels_layerselect_{formatted_data['header']['name']}.json")
            with open(json_path, 'w') as file:
                json.dump(formatted_data, file, indent=4) # Save .json data
            
            self.set_unsaved_changes(False)
            messagebox.showinfo("Success!", f".json file and all layer images exported")
            return True
        return False

    # Save only the .json
    def export_layerselect_json(self):
        try:
            formatted_data = self.format_layer_json("layerselect_save_json")
        except ValueError:
            messagebox.showwarning("Warning!", "Please ensure all text input boxes are filled out correctly.\nIf a number is required, don't enter anything else.")
            return
        except Exception as e:
            messagebox.showerror("Error", e)
            return

        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Json File", "*.json")], initialfile=f"consistxels_layerselect_{formatted_data['header']['name']}.json")
        if path:
            with open(path, 'w') as file:
                json.dump(formatted_data, file, indent=4)
            
            self.set_unsaved_changes(False)
            messagebox.showinfo("Success!", f"{os.path.basename(path)} exported")
            return True
        return False # If nothing was actually saved, and it's intending to quit, assume this is a cancellation, not a close-without-saving

    # Import a valid .json file.
    def import_layerselect_json(self, path: str = None):
        if not path: path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("Json File", "*.json")])
        if path:
            with open(path) as json_file:
                json_data: dict = json.load(json_file)
                
            try:
                header: dict = json_data.get("header")
                search_data: dict = json_data.get("search_data")
                search_type_data: dict = json_data.get("search_type_data")
                generation_data: dict = json_data.get("generation_data")
                layer_data: list = json_data.get("layer_data")
                pose_data: list = json_data.get("pose_data")
                output_folder_path: str = json_data.get("output_folder_path")

                # header
                self.name_entry_input.set(header["name"])

                # in the future, if things are different between versions, do such checks and changes here
                # version = header.get("consistxels_version")

                json_type = header.get("type") # TODO use in final release
                # json_type = header.get("type", ("layerselect_save_folder" if header.get("paths_are_local") else "layerselect_save_json")) # TODO TEMP FOR TESTING, GET RID OF

                self.start_search_in_center.set(search_data.get("start_search_in_center", False))
                self.search_right_to_left.set(search_data.get("search_right_to_left", False))
                self.detect_identical_images.set(search_data.get("detect_identical_images", False))
                self.detect_rotated_images.set(search_data.get("detect_rotated_images", False))
                self.detect_flip_h_images.set(search_data.get("detect_flip_h_images", False))
                self.detect_flip_v_images.set(search_data.get("detect_flip_v_images", False))

                if search_type_data["search_type"] == "Border":
                    self.update_border_color(self.format_color_string(search_type_data["border_color"]))
                elif search_type_data["search_type"] == "Spacing":
                    self.spacing_rows.set(str(search_type_data["spacing_rows"]))
                    self.spacing_columns.set(str(search_type_data["spacing_columns"]))
                    self.spacing_outer_padding.set(str(search_type_data["spacing_outer_padding"]))
                    self.spacing_inner_padding.set(str(search_type_data["spacing_inner_padding"]))
                    self.spacing_x_separation.set(str(search_type_data["spacing_x_separation"]))
                    self.spacing_y_separation.set(str(search_type_data["spacing_y_separation"]))
                
                new_search_type = search_type_data["search_type"]

                if pose_data:
                    self.set_preset_pose_data(pose_data)
                    
                    if (search_type_data["search_type"] != "Preset" and
                    messagebox.askyesno("Wait!", "Pose data was found in this file, but the specified search type ignores it.\nSwitch search type to Preset and use existing pose data?")
                    ):
                        new_search_type = "Preset"
                
                self.search_type_option.set(new_search_type)
                self.search_type_option_selected(new_search_type, False)

                self.automatic_padding_type_option.set(generation_data.get("automatic_padding_type"))

                self.custom_padding_amount.set(generation_data["custom_padding_amount"])

                # delete any current layers
                for i in reversed(range(len(self.layer_data))):
                    del self.layer_data[i]

                if json_type in ["layerselect_save_json", "sheetdata_generated"]:
                    # Reformat layer image paths to have absolute path if this json's paths are relative
                    # (because we do NEED an absolute path, it's just not SAVED that way so this is adding to that JUST FOR READING the data.
                    # hope this makes sense to me later)
                    curr_folder_path = os.path.dirname(path)

                    for layer in layer_data:
                        search_image_path = layer.get("search_image_path")
                        if search_image_path:
                            layer["search_image_path"] = os.path.join(curr_folder_path, search_image_path)
                            
                        source_image_path = layer.get("source_image_path")
                        if source_image_path:
                            layer["source_image_path"] = os.path.join(curr_folder_path, source_image_path)

                self.add_image_layers(layer_data)

                if output_folder_path: self.output_folder_path.set(output_folder_path)

                self.set_unsaved_changes(False)
            except json.JSONDecodeError as e:
                messagebox.showerror("Error importing .json", e) # not sure for what reason i'd need to have these separated, but i guess it's nice to catch 'em
            except Exception as e:
                messagebox.showerror("Error importing .json", e)

    # Generate button has been pressed, so communicate that to main process, and pass along the selected layer info
    def generate_button_pressed(self):
        data = None
        warning_output = ""

        # Lots of checks to make sure all input is valid
        
        for layer in self.layer_data:
            if ((layer.get("search_image_path") and not gui_shared.check_image_valid(layer.get("search_image_path"))[0])
                or (layer.get("source_image_path") and not gui_shared.check_image_valid(layer.get("source_image_path"))[0])):
                messagebox.showwarning("Warning!", "At least one image is invalid. Check that they exist and are the correct filetype.")
                return

        size_check = gui_shared.warn_image_sizes(["Search image", "Source image"],
            [
                [layer.get("search_image_path") for layer in self.layer_data],
                [layer.get("source_image_path") for layer in self.layer_data]
            ]
        )

        if not size_check:
            warning_output += "Please make sure all images are the same size."
        
        # bandaid fix 'cause I don't wanna have to worry about non-search images at all
        already_warned_search = False
        already_warned_cosmetic = False
        already_warned_border = False

        for layer in self.layer_data:
            if not layer.get("search_image_path"):
                
                if layer.get("is_border", False) and not already_warned_border:
                    if warning_output != "": warning_output += "\n\n"
                    warning_output += "Border layer must have an image."
                    already_warned_border = False

                elif layer.get("is_cosmetic_only", False) and not already_warned_cosmetic:
                    if warning_output != "": warning_output += "\n\n"
                    warning_output += "All cosmetic layers must have an image."
                    already_warned_cosmetic = False
                
                elif not already_warned_search:
                    if warning_output != "": warning_output += "\n\n"
                    warning_output += "All normal layers must have a search image."
                    already_warned_search = False

        try:
            data = self.format_layer_json(False)
        except ValueError:
            if warning_output != "": warning_output += "\n\n"
            warning_output += "One or more input fields contains invalid information. Ensure that input fields that require only numbers don't have anything else."
        
        if data:
            if not data.get("layer_data"):
                if warning_output != "": warning_output += "\n\n"
                warning_output += "Please add at least one layer."
        
        if not (self.name_entry_input.get() and self.name_entry_input.get() != ""):
            if warning_output != "": warning_output += "\n\n"
            warning_output += "Please enter a name for this sprite sheet."

        output_folder_path = self.output_folder_path.get()
        if not output_folder_path:
            if warning_output != "": warning_output += "\n\n"
            warning_output += "Please enter an output folder."

        if warning_output != "":
            messagebox.showwarning("Wait!", f"Resolve the following issue(s) before generating:\n\n{warning_output}")
        else:
            try:
                temp_json_data = {"data": data, "output_folder_path": output_folder_path}

                with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_json_file:
                    json.dump(temp_json_data, temp_json_file) # Save data to temporary .json
                    print(json.dumps({"type": "generate_sheet_data", "val": temp_json_file.name.replace('\\', '/')}), flush=True) # Tell main process to generate

            except Exception as e:
                print(json.dumps({"type": "error", "val": e}), flush=True)
    
    # Update progress bar, labels
    def update_progress(self, value, header_text, info_text):
        self.progress_bar["value"] = value
        self.progress_header_label.configure(text=header_text)
        self.progress_info_label.configure(text=info_text)
    
    # Tell main process to cancel generation
    def cancel_generate(self):
        print(json.dumps({"type": "cancel"}), flush=True)
    
    # Styling/button state stuff once generation's confirmed to have begun
    def generate_begun(self):
        self.generate_button.configure(state="disabled")
        self.load_button.configure(state="disabled")
        self.clear_button.configure(state="disabled")
        self.back_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")

    # Styling/button state stuff once generation's confirmed to have ended
    def generate_ended(self):
        self.generate_button.configure(state="normal")
        self.load_button.configure(state="normal")
        self.clear_button.configure(state="normal")
        self.back_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")

        self.set_unsaved_changes(False) # Presumably, if generation has ended, the .json has already been saved. HOWEVER, this also runs if it's been cancelled! So this should not happen in that case. However, I don't wanna worry about that right now. TODO

    # Tell gui.py that there are unsaved changes    
    def set_unsaved_changes(self, new_unsaved_changes = True):
        self.back_button.config(fg=(gui_shared.danger_fg if new_unsaved_changes else gui_shared.fg_color))
        self.set_unsaved_changes_callback(new_unsaved_changes)

        if new_unsaved_changes and self.back_button.cget('state') == 'normal':
            self.update_progress(0, "", "")

    # Called by gui.py
    def save_changes(self):
        return self.export_layerselect_json()
