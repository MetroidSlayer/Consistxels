# TODO TODO TODO: go through and remove unnecessary frames that were there for formatting. can often use 'anchor="w"'

import os
import json
import tempfile
import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox, ttk
from PIL import Image, ImageTk, ImageColor

from tooltip import ToolTip
# from shared import on_global_click, consistxels_version
from shared import consistxels_version

from viewport_canvas import ViewportCanvas

import gui_shared
from gui_shared import add_widget

class Menu_LayerSelect(tk.Frame):
    def __init__(self, master, change_menu_callback, set_unsaved_changes_callback, load_path = None):
        super().__init__(master)

        # Track images and border
        self.layer_data = []  # List of dicts: {path, name, thumbnail, img_obj}
        self.border_color = "#00007f" # in the future, could be taken from info stored from last generation # ALSO could be a tk.StringVar()
        self.image_size = None
        # self.preview_zoom = 1.0
        self.preview_image = None
        # self.formatted_canvas_image = None
        # self.img_id = None

        self.set_unsaved_changes_callback = set_unsaved_changes_callback

        self.configure(bg=gui_shared.bg_color)

        self.after(0, self.setup_ui, change_menu_callback, load_path)

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
        ToolTip(self.load_button, """Load a .json file and restore previous search options and layer data.\n\n(Works with both of the previous 'Save' options, as well as generated pose data output.)""")

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

        paned_window.add(self.left_frame, minsize=417, stretch="never")
        paned_window.add(self.center_frame, minsize=2, stretch="always")
        paned_window.add(self.right_frame, minsize=400, stretch="never")
        
        # Layer options:

        # Layer header
        layer_header = tk.Frame(self.left_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        layer_header.pack(side="top", fill="x")

        # Layer main frame
        layer_main_frame = tk.Frame(self.left_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        layer_main_frame.pack(side="top", fill="both", expand=True)

        # Actual layer menu
        layer_canvas_frame = tk.Frame(layer_main_frame, bg=gui_shared.bg_color, width=0)
        # layer_canvas_frame.pack(side="left", fill="both", expand=True)
        layer_canvas_frame.pack(side="left", fill="both", expand=True)#, pady=5) # TODO instead of this, find way to add +5 pady to top and bottom layer cards. not high priority

        # self.layer_canvas = tk.Canvas(layer_main_frame, bg=gui_shared.bg_color, )
        self.layer_canvas = tk.Canvas(layer_canvas_frame, bg=gui_shared.bg_color, highlightthickness=0, width=0)

        self.layer_scrollbar = tk.Scrollbar(layer_main_frame, orient="vertical", command=self.layer_canvas.yview)
        self.layer_scrollbar.pack(side="left", fill="y", padx=(2,0))

        self.scrollable_frame = tk.Frame(self.layer_canvas, bg=gui_shared.bg_color)

        # Bind scrolling
        self.scrollable_frame.bind("<Configure>", lambda e: self.layer_canvas.configure(scrollregion=self.layer_canvas.bbox("all")))

        # Create canvas in which to show layer info
        self.layer_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.layer_canvas.configure(yscrollcommand=self.layer_scrollbar.set)

        def resize_layer_scrollable_frame(_ = None):
            self.left_frame.update()
            # print({"type":"print", "val":self.scrollable_frame.cget('width')})
            
            self.scrollable_frame.configure(width = layer_canvas_frame.winfo_width())
            # self.layer_canvas.configure(width = self.scrollable_frame.cget('width'))
            # self.layer_canvas.configure(width = self.left_frame.winfo_width()-20)

            # print({"type":"print", "val":self.scrollable_frame.cget('width')})
            # print("gothere")

            # self.redraw_layer_cards()

            for i in range(len(self.layer_data)):
                self.update_layer_card_width(i)
        
        # def resize_layer_canvas(_ = None):
        #     self.left_frame.update()
        #     # print({"type":"print", "val":self.scrollable_frame.cget('width')})
        #     self.layer_canvas.configure(width=self.left_frame.winfo_width()-20)
        #     # print({"type":"print", "val":self.scrollable_frame.cget('width')})
        #     # print("gothere")
        #     self.redraw_image_entries()

        self.left_frame.bind("<Configure>", resize_layer_scrollable_frame)

        self.layer_canvas.pack(side="left", fill="both", expand=True)
        # self.layer_canvas.pack(side="left", fill="y")
        # self.layer_scrollbar.pack(side="right", fill="y")

        # # Mousewheel scrolling
        # self.layer_canvas.bind_all("<MouseWheel>", self.on_mousewheel) # don't do bind ALL, just stuff inside layer_canvas, or maybe inside left_frame

        # Layer footer
        layer_footer = tk.Frame(self.left_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        layer_footer.pack(side="top", fill="x")

        # Top add buttons
        layer_add_blank_top = tk.Button(layer_header, text="➕ Blank layer", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=lambda t=True: self.add_blank_layer(t))
        layer_add_blank_top.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        ToolTip(layer_add_blank_top, "Add a blank layer as the top layer.")

        layer_add_images_top = tk.Button(layer_header, text="➕ From image(s)", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=lambda t=True: self.add_image_layers(add_to_top=t))
        layer_add_images_top.pack(side="right", padx=(0,10), pady=10, fill="x", expand=True)
        ToolTip(layer_add_images_top, "Add image(s) as the top layer(s). Layer's name will be autofilled with its image's filename.")

        # Bottom add buttons (NEED SOME WAY TO MAKE IT ADD TO BOTTOM/TOP CORRECTLY)
        layer_add_blank_bottom = tk.Button(layer_footer, text="➕ Blank layer", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=lambda t=False: self.add_blank_layer(t))
        layer_add_blank_bottom.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        ToolTip(layer_add_blank_bottom, "Add a blank layer as the bottom layer.", True)

        layer_add_images_bottom = tk.Button(layer_footer, text="➕ From image(s)", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=lambda t=False: self.add_image_layers(add_to_top=t))
        layer_add_images_bottom.pack(side="right", padx=(0,10), pady=10, fill="x", expand=True)
        ToolTip(layer_add_images_bottom, "Add image(s) as the bottom layer(s). Layer's name will be autofilled with its image's filename.", True)

        
        # Mousewheel scrolling
        # self.layer_canvas.bind_all("<MouseWheel>", self.on_left_frame_mousewheel) # don't do bind ALL, just stuff inside layer_canvas, or maybe inside left_frame
        gui_shared.bind_event_to_all_children(self.left_frame,"<MouseWheel>",self.on_left_frame_mousewheel)

        # Center preview:

        preview_frame = tk.Frame(self.center_frame, bg=gui_shared.field_bg, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        preview_frame.pack(side="top", fill="both", expand=True)

        preview_frame.grid_rowconfigure(0, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)

        self.preview_viewportcanvas = ViewportCanvas(preview_frame, bg=gui_shared.field_bg, highlightthickness=0, cursor="hand2")
        # self.preview_viewportcanvas.pack(fill="both", expand=True)
        self.preview_viewportcanvas.grid(row=0, column=0, sticky="NSEW")

        # Preview canvas
        # self.preview_canvas = tk.Canvas(self.center_frame, bg=gui_shared.field_bg, highlightthickness=0)
        # self.preview_canvas.pack(side="top", fill="both", expand=True)

        # self.preview_canvas = tk.Canvas(preview_frame, bg=gui_shared.field_bg, highlightthickness=0)
        # self.preview_contents_frame = tk.Frame(self.preview_canvas, bg=gui_shared.field_bg)

        # Canvas scroll bars
        # preview_canvas_vert_scroll = tk.Scrollbar(self.preview_canvas, orient="vertical", command=self.preview_canvas.yview)
        # preview_canvas_vert_scroll = tk.Scrollbar(preview_frame, orient="vertical", command=self.preview_canvas.yview)
        # preview_canvas_vert_scroll.pack(side="right", fill="y")

        # preview_canvas_hori_scroll = tk.Scrollbar(self.preview_canvas, orient="horizontal", command=self.preview_canvas.xview)
        # preview_canvas_hori_scroll = tk.Scrollbar(preview_frame, orient="horizontal", command=self.preview_canvas.xview)
        # preview_canvas_hori_scroll.pack(side="bottom", fill="x")

        # self.preview_canvas.create_window((0, 0), window=self.preview_contents_frame, anchor="center")
        # self.preview_canvas.configure(yscrollcommand=preview_canvas_vert_scroll.set, xscrollcommand=preview_canvas_hori_scroll.set)
        # self.preview_canvas.pack(side="top", fill="both", expand=True)

        # self.preview_canvas.bind("<MouseWheel>", self.on_preview_canvas_mousewheel, add="+")

        # self.preview_contents_frame.bind("<Configure>", lambda e: self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all")))



        # self.style = ttk.Style()
        # self.style.theme_use('default')  # Important: avoid native theme if you want full control
        # self.style.configure("Custom.Vertical.TScrollbar",
        #     troughcolor='gray',
        #     background='blue',
        #     arrowcolor='white'
        # )
        # self.style.configure("Custom.Horizontal.TScrollbar",
        #     troughcolor='gray',
        #     background='blue',
        #     arrowcolor='white'
        # )

        preview_canvas_hori_scroll = tk.Scrollbar(preview_frame, orient="horizontal", command=self.preview_viewportcanvas.scroll_x)
        # preview_canvas_hori_scroll = ttk.Scrollbar(preview_frame, orient="horizontal", command=self.preview_viewportcanvas.scroll_x, style=self.style)
        preview_canvas_hori_scroll.grid(row=1, column=0, sticky="EW")

        preview_canvas_vert_scroll = tk.Scrollbar(preview_frame, orient="vertical", command=self.preview_viewportcanvas.scroll_y)
        # preview_canvas_vert_scroll = ttk.Scrollbar(preview_frame, orient="vertical", command=self.preview_viewportcanvas.scroll_y, style=self.style)
        preview_canvas_vert_scroll.grid(row=0, column=1, sticky="NS")

        self.preview_viewportcanvas.connect_scrollbars(preview_canvas_hori_scroll, preview_canvas_vert_scroll)

        # Canvas buttons have to go *some*where.
        # (would really like this to be ON the canvas at some point.)
        canvas_buttons_frame = tk.Frame(self.center_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        canvas_buttons_frame.pack(side="top", fill="x")

        # Bottomleft reload button
        self.update_preview_button = tk.Button(canvas_buttons_frame, text="Update Preview", command=self.update_preview_image, bg=gui_shared.button_bg, fg=gui_shared.fg_color)
        self.update_preview_button.pack(side="left", padx=10, pady=10) # figure out how to get bottom-left
        ToolTip(self.update_preview_button, """Update the preview image that contains all layers ordered as shown. May take a while if you have a lot of images.\n\n(If the button is yellow, changes have been made, and the preview can be updated.)""", True)

        # Bottomright zoom buttons
        # zoom_in_button = tk.Button(canvas_buttons_frame, text="➕", bg=gui_shared.button_bg, fg=gui_shared.fg_color)
        # zoom_in_button = tk.Button(canvas_buttons_frame, text="➕", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=lambda d=1.0: self.preview_canvas_zoom(d))
        # zoom_in_button.pack(side="right", padx=(5, 10), pady=10)
        # ToolTip(zoom_in_button, "Zoom in", True)

        # zoom_out_button = tk.Button(canvas_buttons_frame, text="➖", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=lambda d=-1.0: self.preview_canvas_zoom(d))
        # zoom_out_button.pack(side="right", padx=(10, 5), pady=10)
        # ToolTip(zoom_out_button, "Zoom out", True)

        # Right menu:

        # I want to find a way to make this more prominent somehow. It's VERY important and shouldn't be missed.
        name_frame = tk.Frame(self.right_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        name_frame.pack(side="top", fill="x")

        name_label = tk.Label(name_frame, text="Sprite sheet name:", bg=gui_shared.bg_color, fg=gui_shared.fg_color)
        name_label.pack(side="left", padx=10, pady=10)

        self.name_entry_input = tk.StringVar()
        # name_entry = tk.Entry(name_frame, bg=gui_shared.field_bg, fg=gui_shared.fg_color, textvariable=self.name_entry_input)
        # name_entry.bind("<FocusIn>", self.on_entry_FocusIn) # this is NOT for saving name info - it's for focusing/unfocusing textbox on global click (i think)
        # name_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        # name_entry.pack(side="left", fill="x", expand=True, padx=(0,10), pady=10)
        # ToolTip(name_entry, "Enter the name of the sprite sheet, which is used to display and organize some information.") # make better desc
        add_widget(
            tk.Entry, name_frame, {'textvariable':self.name_entry_input}, {'text':"Enter the name of the sprite sheet, which is used to display and organize some information."}
        ).pack(side="left", fill="x", expand=True, padx=(0,10), pady=10)

        # Search type

        self.search_types = ["Border", "Spacing", "Preset"]

        search_type_frame = tk.Frame(self.right_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg, height=240)
        search_type_frame.pack(side="top", fill="x")
        search_type_frame.pack_propagate(False)

        search_type_option_frame = tk.Frame(search_type_frame, bg=gui_shared.bg_color)
        search_type_option_frame.pack(side="top", fill="x")

        search_type_label = tk.Label(search_type_option_frame, text="Search type:", bg=gui_shared.bg_color, fg=gui_shared.fg_color)
        search_type_label.pack(side="left", padx=10, pady=10)
        ToolTip(search_type_label, """
- Border: Searches a border image for boxes that contain poses. When selected, a border layer will be automatically created. Add a valid image, with *perfectly rectangular* pose boxes.

- Spacing: Poses are assumed to be spaced out equally from each other.

- Preset: Use a valid .json file that contains pose data (i.e., one generated with the "Generate Pose Data..." button) to search for poses in already-known locations.
        """.strip(), False, True)

        self.search_type_option = tk.StringVar(value=self.search_types[0])

        search_type_subframe_container_frame = tk.Frame(search_type_frame, bg=gui_shared.bg_color)
        search_type_subframe_container_frame.pack(side="top", fill="both", expand=True)

        search_border_subframe = tk.Frame(search_type_subframe_container_frame, bg=gui_shared.bg_color)
        search_border_subframe.place(relx=0, rely=0, relwidth=1, relheight=1)

        search_spacing_subframe = tk.Frame(search_type_subframe_container_frame, bg=gui_shared.bg_color)
        search_spacing_subframe.place(relx=0, rely=0, relwidth=1, relheight=1)

        search_preset_subframe = tk.Frame(search_type_subframe_container_frame, bg=gui_shared.bg_color)
        search_preset_subframe.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.search_type_subframes = [search_border_subframe, search_spacing_subframe, search_preset_subframe]

        # def search_type_option_selected(selected_option, set_unsaved_changes = True):
        #     search_type_subframes[self.search_types.index(selected_option)].lift()

        #     if selected_option == "Border":
        #         self.add_border_layer() # TODO This should ONLY run if something has actually changed
        #     else:
        #         border_index = next((i for i, layer in enumerate(self.layer_data) if layer["is_border"]), None)
        #         if border_index != None: self.delete_layer(border_index)
            
        #     if set_unsaved_changes: # hackey solution to making this not run upon creating new menu.
        #         # I'd prefer to have this ONLY if something's actually changed.
        #        self.set_unsaved_changes(True)

        self.search_type_option_selected("Border", False)

        # search_type_optionmenu = tk.OptionMenu(search_type_option_frame, self.search_type_option, *self.search_types, command=search_type_option_selected)
        search_type_optionmenu = tk.OptionMenu(search_type_option_frame, self.search_type_option, *self.search_types, command=self.search_type_option_selected)
        # something to make the border stuff show up in the layers section (see above, i think)
        search_type_optionmenu.configure(bg=gui_shared.field_bg, fg=gui_shared.fg_color, activebackground=gui_shared.bg_color, activeforeground=gui_shared.fg_color, anchor="w", justify="left", highlightthickness=1, highlightbackground=gui_shared.secondary_fg, bd=0, relief="flat")
        search_type_optionmenu["menu"].configure(bg=gui_shared.field_bg, fg=gui_shared.fg_color, activebackground=gui_shared.secondary_bg, activeforeground=gui_shared.fg_color)
        search_type_optionmenu.pack(side="left", padx=(0,10), pady=10, fill="x", expand=True)
        ToolTip(search_type_optionmenu, """
- Border: Searches a border image for boxes that contain poses. When selected, a border layer will be automatically created. Add a valid image with *perfectly rectangular* pose boxes.

- Spacing: Poses are assumed to be spaced out equally from each other.

- Preset: Use a valid .json file that contains pose data (i.e., one generated with the "Generate Pose Data..." button) to search for poses in already-known locations.
        """.strip(), False, True)

        # Border subframe

        # choose_border_button = tk.Button(search_border_subframe, text="Choose Border", command=self.add_border, bg=gui_shared.button_bg, fg=gui_shared.fg_color)
        # choose_border_button.grid(padx=10, pady=10, row=0, column=1)
        # ToolTip(choose_border_button, "Choose an image file containing the borders of the sprites' poses. This will be searched in order to find the poses and generate the data.")

        # self.border_label = tk.Label(search_border_subframe, text="No border selected", bg=gui_shared.bg_color, fg=gui_shared.fg_color)
        # self.border_label.grid(padx=0, pady=10, row=0, column=2)

        tk.Label(search_border_subframe, text="Border Color:", bg=gui_shared.bg_color, fg=gui_shared.fg_color).grid(padx=5, pady=5, row=1, column=1)

        border_color_input_frame = tk.Frame(search_border_subframe, bg=gui_shared.bg_color)
        border_color_input_frame.grid(row=1, column=2)

        self.border_color_swatch = tk.Canvas(border_color_input_frame, width=20, height=20, bg=self.border_color,
        highlightthickness=1, highlightbackground="black")
        self.border_color_swatch.pack(side="left", padx=5, pady=5)

        self.color_entry_input = tk.StringVar()
        self.color_entry_input.set(self.format_color_string(self.border_color))
        
        # color_entry = tk.Entry(border_color_swatch_and_entry_frame, width=10, bg=gui_shared.field_bg, fg=gui_shared.fg_color, textvariable=self.color_entry_input)
        # color_entry.bind("<FocusIn>", self.on_entry_FocusIn)
        # color_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        # color_entry.bind("<FocusOut>", self.border_color_entry_input, add="+")
        # color_entry.pack(side="left", padx=5, pady=5)
        # ToolTip(color_entry, "Type the color that will be interpreted as the border.")
        color_entry = add_widget(
            tk.Entry, border_color_input_frame, {'width':10, 'textvariable':self.color_entry_input}, {'text':"Type the color that will be interpreted as the border."}
        )
        color_entry.pack(side="left", padx=5, pady=5)
        color_entry.bind("<FocusOut>", self.border_color_entry_input, add="+")

        pick_border_color_button = tk.Button(search_border_subframe, text="Open Color Picker", command=self.pick_color, bg=gui_shared.button_bg, fg=gui_shared.fg_color)
        pick_border_color_button.grid(padx=5, pady=5, row=1, column=3)
        ToolTip(pick_border_color_button, "Open a color picker and pick the color that will be interpreted as the border.") # would be better if it relied on detected border color!

        # Spacing subframe
        # (This would all look a LOT better if it was gridded rather than packed. look into it)

        search_spacing_subframe.grid_anchor("center")
        search_spacing_subframe.grid_columnconfigure(0, weight=1)

        # Grid frame
        # spacing_grid_frame = tk.Frame(search_spacing_subframe, bg=gui_shared.bg_color)
        # spacing_grid_frame.pack(side="top", fill="x")

        # tk.Label(spacing_grid_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Grid:   Rows:").pack(side="left", padx=(10,5), pady=10)
        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Grid:").grid(row=0, column=0, padx=10, pady=10, sticky="W")
        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Rows:").grid(row=0, column=1, pady=10, sticky="E")
        
        self.spacing_rows = tk.StringVar()
        self.spacing_rows.set("0")

        # spacing_grid_rows_entry = tk.Entry(grid_frame, bg=gui_shared.field_bg, fg=gui_shared.fg_color, width=6, textvariable=self.spacing_grid_rows)
        # spacing_grid_rows_entry.pack(side="left", pady=10)
        # spacing_grid_rows_entry.bind("<FocusIn>", self.on_entry_FocusIn)
        # spacing_grid_rows_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        # ToolTip(spacing_grid_rows_entry, "How many rows does the sprite sheet have?", False, True)
        add_widget(
        #     tk.Entry, spacing_grid_frame, {'width':6, 'textvariable':self.spacing_rows}, {'text':"How many rows does the sprite sheet have?"}
        # ).pack(side="left", pady=10)
            tk.Entry, search_spacing_subframe, {'width':6, 'textvariable':self.spacing_rows}, {'text':"How many rows does the sprite sheet have?"}
        ).grid(row=0, column=2, padx=5, pady=10)

        # tk.Label(spacing_grid_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="   Columns:").pack(side="left", padx=5, pady=10)
        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Columns:").grid(row=0, column=4, pady=10, sticky="E")

        self.spacing_columns = tk.StringVar()
        self.spacing_columns.set("0")

        # spacing_grid_columns_entry = tk.Entry(spacing_grid_frame, bg=gui_shared.field_bg, fg=gui_shared.fg_color, width=6, textvariable=self.spacing_grid_columns)
        # spacing_grid_columns_entry.pack(side="left", pady=10)
        # spacing_grid_columns_entry.bind("<FocusIn>", self.on_entry_FocusIn)
        # spacing_grid_columns_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        # ToolTip(spacing_grid_columns_entry, "How many columns does the sprite sheet have?", False, True)
        add_widget(
        #     tk.Entry, spacing_grid_frame, {'width':6, 'textvariable':self.spacing_columns}, {'text':"How many columns does the sprite sheet have?"}
        # ).pack(side="left", pady=10)
            tk.Entry, search_spacing_subframe, {'width':6, 'textvariable':self.spacing_columns}, {'text':"How many columns does the sprite sheet have?"}
        ).grid(row=0, column=5, padx=(5,10), pady=10)

        # Outer padding
        # spacing_padding_frame = tk.Frame(search_spacing_subframe, bg=gui_shared.bg_color)
        # spacing_padding_frame.pack(side="top", fill="x")

        # tk.Label(spacing_padding_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Padding:   Outer:").pack(side="left", padx=(10,5), pady=10)
        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Padding:").grid(row=1, column=0, padx=10, pady=10, sticky="W")
        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Outer:").grid(row=1, column=1, pady=10, sticky="E")

        self.spacing_outer_padding = tk.StringVar()
        self.spacing_outer_padding.set("0")

        # outer_padding_entry = tk.Entry(spacing_padding_frame, bg=gui_shared.field_bg, fg=gui_shared.fg_color, width=6, textvariable=self.outer_padding)
        # outer_padding_entry.pack(side="left")
        # outer_padding_entry.bind("<FocusIn>", self.on_entry_FocusIn)
        # outer_padding_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        # ToolTip(outer_padding_entry, "How much space between the sprites and the edge of the sprite sheet?\n(NOT to be confused with the automatic and custom padding - Outer and inner are\nfor the input images, automatic and custom are for the output images)", False, True)
        add_widget(
        #     tk.Entry, spacing_padding_frame, {'width':6, 'textvariable':self.spacing_outer_padding}, {'text':"""How much space between the sprites and the edge of the sprite sheet?\n\n(NOT to be confused with the automatic and custom padding - outer and inner are for the input layer images, automatic and custom are for the output pose images)"""}
        # ).pack(side="left", pady=10)
            tk.Entry, search_spacing_subframe, {'width':6, 'textvariable':self.spacing_outer_padding}, {'text':"""How much space between the sprites and the edge of the sprite sheet?\n\n(NOT to be confused with the automatic and custom padding - outer and inner are for the input layer images, automatic and custom are for the output pose images)"""}
        ).grid(row=1, column=2, padx=5, pady=10)

        # tk.Label(spacing_padding_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="px").pack(side="left", padx=(5,10), pady=10)

        # Inner padding
        # inner_padding_frame = tk.Frame(search_spacing_subframe, bg=gui_shared.bg_color)
        # inner_padding_frame.pack(side="top", fill="x")

        # tk.Label(spacing_padding_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="px   Inner:").pack(side="left", padx=5, pady=10)
        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="px").grid(row=1, column=3, padx=(0,10), pady=10, sticky="W")
        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Inner:").grid(row=1, column=4, pady=10, sticky="E")

        self.spacing_inner_padding = tk.StringVar()
        self.spacing_inner_padding.set("0")
        # inner_padding_entry = tk.Entry(spacing_padding_frame, bg=gui_shared.field_bg, fg=gui_shared.fg_color, width=6, textvariable=self.inner_padding)
        # inner_padding_entry.pack(side="left", pady=10)
        # inner_padding_entry.bind("<FocusIn>", self.on_entry_FocusIn)
        # inner_padding_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        # ToolTip(inner_padding_entry, "How much extra padding around each sprite?\n(NOT to be confused with the automatic and custom padding - Outer and inner are\nfor the input images, automatic and custom are for the output images)", False, True)
        add_widget(
        #     tk.Entry, spacing_padding_frame, {'width':6, 'textvariable':self.spacing_inner_padding}, {'text':"""How much extra padding around each sprite?\n\n(NOT to be confused with the automatic and custom padding - outer and inner are for the input layer images, automatic and custom are for the output pose images)"""}
        # ).pack(side="left", pady=10)
            tk.Entry, search_spacing_subframe, {'width':6, 'textvariable':self.spacing_inner_padding}, {'text':"""How much extra padding around each sprite?\n\n(NOT to be confused with the automatic and custom padding - outer and inner are for the input layer images, automatic and custom are for the output pose images)"""}
        ).grid(row=1, column=5, padx=5, pady=10)


        # tk.Label(spacing_padding_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="px").pack(side="left", padx=(5,10), pady=10)
        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="px").grid(row=1, column=6, padx=(0,10), pady=10, sticky="W")

        # Separation
        # spacing_separation_frame = tk.Frame(search_spacing_subframe, bg=gui_shared.bg_color)
        # spacing_separation_frame.pack(side="top", fill="x")

        # tk.Label(spacing_separation_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Separation:   x").pack(side="left", padx=(10,5), pady=10)
        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Separation:").grid(row=2, column=0, padx=10, pady=10, sticky="W")
        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="x:").grid(row=2, column=1, pady=10, sticky="E")
        
        self.spacing_x_separation = tk.StringVar()
        self.spacing_x_separation.set("0")

        # x_separation_entry = tk.Entry(separation_frame, bg=gui_shared.field_bg, fg=gui_shared.fg_color, width=6, textvariable=self.spacing_x_separation)
        # x_separation_entry.pack(side="left", pady=10)
        # x_separation_entry.bind("<FocusIn>", self.on_entry_FocusIn)
        # x_separation_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        # ToolTip(x_separation_entry, "How much horizontal space between each sprite?", False, True)
        add_widget(
        #     tk.Entry, spacing_separation_frame, {'width':6, 'textvariable':self.spacing_x_separation}, {'text':"How much horizontal space between each sprite?"}
        # ).pack(side="left", pady=10)
            tk.Entry, search_spacing_subframe, {'width':6, 'textvariable':self.spacing_x_separation}, {'text':"How much horizontal space between each sprite?"}
        ).grid(row=2, column=2, padx=5, pady=10)

        # tk.Label(spacing_separation_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="px   y").pack(side="left", padx=5, pady=10)
        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="px").grid(row=2, column=3, padx=(0,10), pady=10, sticky="W")
        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="y:").grid(row=2, column=4, pady=10, sticky="E")

        self.spacing_y_separation = tk.StringVar()
        self.spacing_y_separation.set("0")
        # y_separation_entry = tk.Entry(spacing_separation_frame, bg=gui_shared.field_bg, fg=gui_shared.fg_color, width=6, textvariable=self.spacing_y_separation)
        # y_separation_entry.pack(side="left", pady=10)
        # y_separation_entry.bind("<FocusIn>", self.on_entry_FocusIn)
        # y_separation_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        # ToolTip(y_separation_entry, "How much vertical space between each sprite?", False, True)
        add_widget(
        #     tk.Entry, spacing_separation_frame, {'width':6, 'textvariable':self.spacing_y_separation}, {'text':"How much vertical space between each sprite?"}
        # ).pack(side="left", pady=10)
            tk.Entry, search_spacing_subframe, {'width':6, 'textvariable':self.spacing_y_separation}, {'text':"How much vertical space between each sprite?"}
        ).grid(row=2, column=5, padx=5, pady=10)

        # tk.Label(spacing_separation_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="px").pack(side="left", padx=(5,10), pady=10)
        tk.Label(search_spacing_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="px").grid(row=2, column=6, padx=(0,10), pady=10, sticky="W")

        # Preset Subframe

        # preset_input_frame = tk.Frame(search_preset_subframe, bg=gui_shared.bg_color)
        # preset_input_frame.pack(side="top", fill="x")

        search_preset_subframe.grid_columnconfigure(1, weight=1)

        # tk.Label(preset_input_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Preset:").pack(side="left", padx=(10,5), pady=10)
        tk.Label(search_preset_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Preset:").grid(row=0, column=0, sticky="W", padx=(10,5), pady=10)

        self.preset_path = tk.StringVar()

        # preset_path_entry = tk.Entry(preset_input_frame, bg=gui_shared.field_bg, fg=gui_shared.fg_color, textvariable=self.preset_path)
        # preset_path_entry.pack(side="left", pady=10, fill="x", expand=True)
        # preset_path_entry.bind("<FocusIn>", self.on_entry_FocusIn)
        # preset_path_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        # ToolTip(preset_path_entry, "Enter the preset's path. (Preset should be a .json that contains pose data.)", False, True)
        preset_entry = add_widget(
            # tk.Entry, preset_input_frame, {'textvariable':self.preset_path}, {'text':"How much vertical space between each sprite?"}
            tk.Entry, search_preset_subframe, {'width':1, 'textvariable':self.preset_path}, {'text':"How much vertical space between each sprite?"}
        )
        # preset_entry.pack(side="left", pady=10, fill="x", expand=True)
        preset_entry.grid(row=0, column=1, sticky="EW", pady=10)
        ToolTip(preset_entry, "Enter a path of a preset.  (Preset should be a .json that contains pose data.)")

        # def open_preset_json():
        #     path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("Json File", "*.json")])
        #     if path:
        #         self.preset_path.set(path)
        #         # preset_entry.xview("end")

        # preset_pick_button = tk.Button(preset_input_frame, bg=gui_shared.button_bg, fg=gui_shared.fg_color, text="📁", command=open_preset_json)
        # preset_pick_button.pack(side="left", padx=10, pady=5)

        self.preset_pose_data = None

        preset_pick_button = tk.Button(search_preset_subframe, bg=gui_shared.button_bg, fg=gui_shared.fg_color, text="📁", command=self.load_preset_json)
        preset_pick_button.grid(row=0, column=2, sticky="E", padx=10, pady=5)
        ToolTip(preset_pick_button, "Choose a preset. (Preset should be a .json that contains pose data.)", False, True)

        self.preset_load_label = tk.Label(search_preset_subframe, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="No preset loaded", justify="left")
        self.preset_load_label.grid(row=1, column=0, columnspan=3, sticky="W", padx=10, pady=(0,10))

        # Search options

        search_options_frame = tk.Frame(self.right_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        # search_options_frame.pack(side="top", fill="x")
        search_options_frame.pack(side="top", fill="both", expand=True)

        search_options_checkboxes_frame = tk.Frame(search_options_frame, bg=gui_shared.bg_color)
        # search_options_checkboxes_frame.pack(side="top", fill="x", expand=True)
        search_options_checkboxes_frame.pack(side="top", fill="x")

        search_options_checkboxes_frame.grid_anchor("center")

        self.start_search_in_center = tk.BooleanVar()
        start_search_in_center_checkbutton = tk.Checkbutton(search_options_checkboxes_frame, text="Start search in center", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, variable=self.start_search_in_center, command=self.set_unsaved_changes)
        start_search_in_center_checkbutton.grid(row=0, column=0, padx=10, pady=5)
        start_search_in_center_checkbutton.select()
        ToolTip(start_search_in_center_checkbutton, """When searching the spritesheet, the program will look at each row starting in the middle of the image, rather than at the edge. It will search outward in one direction before reaching the edge, at which point it will search in the other direction, before moving onto the next row.\n\nRecommended for sprite sheets that group poses in a vertical formation, as it makes the order that pose images are found in much more intuitive. Not recommended if "Search right-to-left" is enabled.""")
        
        self.search_right_to_left = tk.BooleanVar()
        search_right_to_left_checkbutton = tk.Checkbutton(search_options_checkboxes_frame, text="Search right-to-left", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, variable=self.search_right_to_left, command=self.set_unsaved_changes)
        search_right_to_left_checkbutton.grid(row=0, column=1, padx=10, pady=5)
        ToolTip(search_right_to_left_checkbutton, """Search the spritesheet from right-to-left, instead of from left-to-right.\n\nRecommended if "Start search in center" is disabled, as most characters face right by default, and most sprite sheets show the rightmost sprites on the right side of the sheet, so the generated data will use the right-facing poses as the defaults. Not recommended otherwise.""")

        # detect identical images
        self.detect_identical_images = tk.BooleanVar()
        detect_identical_images_checkbutton = tk.Checkbutton(search_options_checkboxes_frame, text="Detect identical images", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, variable=self.detect_identical_images, command=self.set_unsaved_changes)
        detect_identical_images_checkbutton.grid(row=1, column=0, padx=10, pady=(10,5))
        detect_identical_images_checkbutton.select()
        ToolTip(detect_identical_images_checkbutton, """Check if poses use already-found pose images, so they can share the same pose image.\n\n(Highly recommended - this is kinda the whole point)""")

        # When both flip_h and rotated are selected, flip_v is redundant and therefore disabled for clarity
        def check_flip_v_allowed():
            # if self.detect_rotated_images.get() and self.detect_flip_h_images.get():
            #     self.detect_flip_v_images.set(False)
            #     detect_flip_v_images_checkbutton.configure(state='disabled')
            # else:
            #     detect_flip_v_images_checkbutton.configure(state='normal') # TODO TEST!
            if self.detect_rotated_images.get():
                self.detect_flip_v_images.set(False)
                detect_flip_v_images_checkbutton.configure(state='disabled')
            else:
                detect_flip_v_images_checkbutton.configure(state='normal')

        # detect rotated images
        self.detect_rotated_images = tk.BooleanVar()
        detect_rotated_images_checkbutton = tk.Checkbutton(search_options_checkboxes_frame, text="Detect rotated images", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, variable=self.detect_rotated_images, command=lambda: [check_flip_v_allowed(), self.set_unsaved_changes()])
        detect_rotated_images_checkbutton.grid(row=1, column=1, padx=10, pady=(10,5))
        detect_rotated_images_checkbutton.select()
        ToolTip(detect_rotated_images_checkbutton, "Check if poses use rotated versions of already-found pose images.")

        # detect horizontally mirrored images
        self.detect_flip_h_images = tk.BooleanVar()
        detect_flip_h_images_checkbutton = tk.Checkbutton(search_options_checkboxes_frame, text="Detect horizontally mirrored images", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, variable=self.detect_flip_h_images, command=lambda: [check_flip_v_allowed(), self.set_unsaved_changes()])
        detect_flip_h_images_checkbutton.grid(row=2, column=0, columnspan=2, padx=10, pady=5)
        detect_flip_h_images_checkbutton.select()
        ToolTip(detect_flip_h_images_checkbutton, "Check if poses use horizontally-flipped versions of already-found pose images.")
        
        # detect vertically mirrored images
        self.detect_flip_v_images = tk.BooleanVar()
        detect_flip_v_images_checkbutton = tk.Checkbutton(search_options_checkboxes_frame, text="Detect vertically mirrored images", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, variable=self.detect_flip_v_images, state='disabled', command=self.set_unsaved_changes)
        detect_flip_v_images_checkbutton.grid(row=3, column=0, columnspan=2, padx=10, pady=(5,10))
        # ToolTip(detect_flip_v_images_checkbutton, """Check if poses use vertically-flipped versions of already-found pose images.\n\n(Automatically disabled when using both "detect rotated" and "detect hori. mirrored" to avoid redundancy; a horizontally-flipped, 180-degrees-rotated image is identical to a vertically-flipped image.)""")
        ToolTip(detect_flip_v_images_checkbutton, """Check if poses use vertically-flipped versions of already-found pose images.\n\n(Automatically disabled when using "detect rotated" to avoid redundancy; a horizontally-flipped, 180-degrees-rotated image is identical to a vertically-flipped image, so just use "detect rotated" with "detect h-mirrored" instead.)""")

        # Generation

        # generate empty poses
        # Determine whether pose data will be created for completely-empty pose boxes.
        self.generate_empty_poses = tk.BooleanVar()
        generate_empty_poses_checkbutton = tk.Checkbutton(search_options_checkboxes_frame, text="Generate empty poses", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, variable=self.generate_empty_poses, command=self.set_unsaved_changes)
        generate_empty_poses_checkbutton.grid(row=4, column=0, columnspan=2, padx=10, pady=(5,10))
        ToolTip(generate_empty_poses_checkbutton, "Determine whether pose data will be created for pose boxes that are completely empty.")

        # export versions of layers with only unique pose images???
        # (might be good to have this as a setting here. i think so, at least)

        self.padding_types = ["Show only always-visible pixels", "Show all theoretically-visible pixels", "None"]

        padding_label = tk.Label(search_options_frame, text="Automatic padding type:", bg=gui_shared.bg_color, fg=gui_shared.fg_color)
        padding_label.pack(side="top", padx=10, pady=10)
        # ToolTip(padding_label, "- Show only always-visible pixels: Padding for pose images will increase to show how much space is visible in all instances of that pose image. (Recommended)\n\n- Show all theoretically-visible pixels: Same as above, but padding also contains space that is not visible in some pose boxes.\n\n- None: No extra automatic padding is applied. Recommended if using the \"Custom padding\" option.")

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
        # custom_padding_frame.pack(side="top", fill="x", expand=True)
        # custom_padding_frame.pack(side="top", fill="x")
        custom_padding_frame.pack(side="top")

        tk.Label(custom_padding_frame, text="Custom padding amount:", bg=gui_shared.bg_color, fg=gui_shared.fg_color).pack(side="left", padx=(10,5), pady=10)

        self.custom_padding_amount = tk.StringVar()
        self.custom_padding_amount.set("0")
        # self.custom_padding = tk.IntVar()
        # self.custom_padding.set(0)
        # custom_padding_entry = tk.Entry(custom_padding_frame, bg=gui_shared.field_bg, fg=gui_shared.fg_color, textvariable=self.custom_padding, width=8) # string values will mess everything up!
        # custom_padding_entry.pack(side="left", padx=(5,0))
        # custom_padding_entry.bind("<FocusIn>", self.on_entry_FocusIn)
        # custom_padding_entry.bind("<FocusOut>", self.on_entry_FocusOut)
        # ToolTip(custom_padding_entry, "Enter a custom amount of padding to apply to each pose image. If used alongside automatic padding, this will add the automatic and custom padding together.\n(Negative values are allowed, and will instead subtract from automatic padding without cutting off any of the pose images.)")
        add_widget(
            tk.Entry, custom_padding_frame, {'width':6, 'textvariable':self.custom_padding_amount}, {'text':"""Enter a custom amount of padding to apply to each pose image. If used alongside automatic padding, this will add the automatic and custom padding together.\n\n(Negative values are allowed, and will instead subtract from automatic padding without cutting off any of the pose images.)"""}
        ).pack(side="left", pady=10)

        generate_frame = tk.Frame(self.right_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        # generate_frame.pack(side="bottom", fill="both", expand=True)
        generate_frame.pack(side="bottom", fill="x")

        generate_options_frame = tk.Frame(generate_frame, bg=gui_shared.bg_color)
        generate_options_frame.pack(side="top", fill="x")

        tk.Label(generate_options_frame, text="Output folder path:", bg=gui_shared.bg_color, fg=gui_shared.fg_color).pack(side="left", padx=(10,5), pady=10)

        # checkboxes and entries and such
        # some sort of function to check if folder is empty, and warn user if not
        self.output_folder_path = tk.StringVar()
        output_folder_entry = add_widget(
            tk.Entry, generate_options_frame, {'textvariable':self.output_folder_path, 'width':1}, {'text':"""Enter the path to the folder where the pose images and .json data will be output.\n\n(It's recommended that you choose a new, EMPTY folder! Choosing an existing one will clutter up your files at best, and overwrite existing data at worst. That said, if you WANT to overwrite existing data, go for it.)"""}
        )
        output_folder_entry.pack(side="left", fill="x", expand=True, pady=10)

        def select_output_folder_path():
            # self.output_folder_path.set(filedialog.askdirectory(title="Select an output folder (preferably empty)"))
            path = filedialog.askdirectory(title="Select an output folder (preferably empty)")
            # if os.listdir(path):
            #     messagebox.askyesno()
            if path and ((not os.listdir(path)) or gui_shared.warn_overwrite()):
                self.output_folder_path.set(path)
                # output_folder_entry.xview("end")

        output_folder_button = tk.Button(generate_options_frame, text="📁", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=select_output_folder_path)
        output_folder_button.pack(side="left", padx=10, pady=10)
        ToolTip(output_folder_button, """Open a file dialog and select the folder where the pose images and .json data will be output.\n\n(It's recommended that you choose a new, EMPTY folder! Choosing an existing one will clutter up your files at best, and overwrite existing data at worst. That said, if you WANT to overwrite existing data, go for it.)""")

        generate_container_frame = tk.Frame(generate_frame, bg=gui_shared.bg_color)
        generate_container_frame.pack(side="top", fill="x")

        # generate_buttons_frame = tk.Frame(generate_frame, bg=gui_shared.bg_color)
        generate_buttons_frame = tk.Frame(generate_container_frame, bg=gui_shared.bg_color)
        generate_buttons_frame.pack(side="left")

        # self.generate_button = tk.Button(search_options_frame, text="Generate Pose Data...", command=self.generate_output, bg=gui_shared.button_bg, fg=gui_shared.fg_color)
        # self.generate_button = tk.Button(search_options_frame, text="Generate Pose Data...", command=self.TEST_generate_button_pressed, bg=gui_shared.button_bg, fg=gui_shared.fg_color)
        self.generate_button = tk.Button(generate_buttons_frame, text="Generate Pose Data...", command=self.generate_button_pressed, bg=gui_shared.button_bg, fg=gui_shared.fg_color)
        self.generate_button.pack(side="top", padx=10, pady=10)
        # self.generate_button.grid(padx=10, pady=10, row=0, column=0)
        ToolTip(self.generate_button, "Generate data! (May take a while)", True)

        # for safety i guess
        # self.generate_process = None

        # disable if no process!!!
        self.cancel_button = tk.Button(generate_buttons_frame, text="Cancel", command=self.cancel_generate, fg=gui_shared.danger_fg, bg=gui_shared.button_bg, state="disabled")
        self.cancel_button.pack(side="top", padx=10, pady=(0,10), fill="x")
        ToolTip(self.cancel_button, "Cancel pose image generation", True)
        # self.cancel_button.grid(padx=10, pady=(0,10), row=1, column=0)

        # generate_progress_frame = tk.Frame(generate_frame, bg=gui_shared.bg_color)
        generate_progress_frame = tk.Frame(generate_container_frame, bg=gui_shared.bg_color)
        generate_progress_frame.pack(side="left", fill="x", expand=True)

        self.progress_header_label = tk.Label(generate_progress_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color)
        self.progress_header_label.pack(side="top", padx=(0,10), pady=(10,0), fill="x", expand=True)

        # self.progress_label = tk.Label(search_options_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="")
        self.progress_info_label = tk.Label(generate_progress_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color)
        self.progress_info_label.pack(side="top", padx=(0,10), pady=(0,5), fill="x", expand=True)
        # self.progress_label.grid(padx=10, pady=10, row=0, column=1, columnspan=2)

        # self.progress_bar = ttk.Progressbar(search_options_frame, orient="horizontal", maximum=100)
        self.progress_bar = ttk.Progressbar(generate_progress_frame, orient="horizontal", maximum=100)
        self.progress_bar.pack(padx=(0,10), pady=(0,10), side="top", fill="x", expand=True)
        # self.progress_label.grid(padx=10, pady=10, row=1, column=1, columnspan=2)

        # TODO TODO TODO: some weird stuff with scrolling. i think the preview canvas scrollbar still scrolls the layer canvas

        # self.bind_all("<Button-1>", on_global_click, add="+")
        self.bind_all("<Button-1>", gui_shared.on_global_click, add="+")

        if load_path:
            self.import_layerselect_json(load_path)

        # resize_layer_scrollable_frame()

    # def clear_all(self, change_menu_callback): # TODO test if this even works tbh. ALSO will definitely be easier to just... create an entirely new menu, btw

        # self.layer_data = {}
        # self.layer_thumbnails = []

        # search option
        # border color
        # spacing entries

        # self.start_search_in_center.set(True)
        # self.search_right_to_left.set(False)
        # self.detect_identical_images.set(True)
        # self.detect_rotated_images.set(True)
        # self.detect_flip_h_images.set(True)
        # self.detect_flip_v_images.set(False)

        # entries, idk

    def on_left_frame_mousewheel(self, event):
        delta = -1 * (event.delta // 120)
        self.layer_canvas.yview_scroll(delta, "units")

    # def on_entry_FocusIn(self, event):
    #     event.widget.configure(bg=gui_shared.secondary_bg)
    
    # def on_entry_FocusOut(self, event):
    #     event.widget.configure(bg=gui_shared.field_bg)

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

            self.set_unsaved_changes(True)
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

    def force_get_image_size(self):
        for layer in self.layer_data:
            path = layer.get("search_image_path", layer.get("source_image_path")) # if no search img, get source img. if neither, it's None

            if path:
                with Image.open(path) as image:
                    self.image_size = image.size
                    break # or mabye return new image size? idk

    # def check_image_valid(self, image_path):
    #     try:
    #         with Image.open(image_path) as image:
    #             if self.image_size == None:
    #                 self.image_size = image.size
    #             elif self.image_size != image.size:
    #                 messagebox.showwarning("Warning!", f"All images must be the same size.\nThe detected sprite sheet size is {self.image_size[0]}x{self.image_size[1]}, but a selected image is {image.size[0]}x{image.size[1]}.)")
    #                 return False
    #             return True
    #     except Image.UnidentifiedImageError:
    #         messagebox.showwarning("Warning!", "Please select a valid image.")
    #         return False


    def add_blank_layer(self, add_to_top = True):
        blank_layer = {
            "name": None,
            "is_border": None,
            "is_cosmetic_only": None,
            "search_image_path": None,
            "source_image_path": None
        }
        
        if add_to_top:
            self.layer_data.insert(0, blank_layer)
            # self.layer_thumbnails.insert(0, None)
        else:
            self.layer_data.append(blank_layer)
            # self.layer_thumbnails.append(None)

        self.set_unsaved_changes(True)

        self.redraw_all_layer_cards()

    def add_image_layers(self, data = None, add_to_top = True):
        # paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])


        if not data:
            paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])

            # data["path"] = 
            # data["name"] =
            data = []
            for path in paths:
                # data.append({"path": search_image_path, "name": os.path.splitext(os.path.basename(search_image_path))[0], "alt_source": None})
                data.append({"name": os.path.splitext(os.path.basename(path))[0], "search_image_path": path})
        # else:
        #     paths = []
        #     for d in data:
        #         # paths.append(d["path"])
        #         pass
        # image_size = None

        # for i, path in enumerate(paths):
        # for d in data:
        for d in (reversed(data) if add_to_top else data):
        # for i in (range(data) if add_to_top else range(data, -1, -1)):



            # filename = os.path.basename(path)
            # name = os.path.splitext(filename)[0]
            
            name = d.get("name")
            is_border = d.get("is_border")
            is_cosmetic_only = d.get("is_cosmetic_only")
            search_image_path = d.get("search_image_path")
            source_image_path = d.get("source_image_path")
            export_layer_images = d.get("export_layer_images")

            # name = data[i].get("name")
            # is_border = data[i].get("is_border")
            # is_cosmetic_only = data[i].get("is_cosmetic_only")
            # search_image_path = data[i].get("search_image_path")
            # source_image_path = data[i].get("source_image_path")

            # image = Image.open(search_image_path)
            # with Image.open(search_image_path) as image:
            #     thumb = image.copy()

            # if search_image_path: # TODO TODO TODO think of way to add this to card function versions of adding images. this is an important check!
            #     with Image.open(search_image_path) as search_image:
            #         search_image_size = search_image.size

            #     if self.image_size == None:
            #         self.image_size = search_image_size
            #     elif self.image_size != search_image_size:
            #         messagebox.showwarning("Warning!", "All images must be the same size")
            #         break

            # if source_image_path:
            #     with Image.open(source_image_path) as source_image:
            #         source_image_size = source_image.size

            #     if self.image_size == None:
            #         self.image_size = source_image_size
            #     elif self.image_size != source_image_size:
            #         messagebox.showwarning("Warning!", "All images must be the same size")
            #         break

            # if len(self.layer_data):
            #     if self.layer_data[0]["img"].size != thumb.size:
            #         image.close()
            #         messagebox.showwarning("Warning", "All images must be the same size")
            #         break
            # if self.border_image != None:
            #     if self.border_image.size != thumb.size:
            #         image.close()
            #         messagebox.showwarning("Warning", "All images must be the same size as the border")
            #         break

            # might want to move thumbnail stuff to redraw_image_entries(), but then we'll have to reopen the images and everything... not actually that bad i think
            # thumb.thumbnail((64, 64))
            # photo = ImageTk.PhotoImage(thumb)
            
            new_layer = {
                "name": name,
                "search_image_path": search_image_path,
                "source_image_path": source_image_path,
                "is_border": is_border == True,
                "is_cosmetic_only": is_cosmetic_only == True,
                "export_layer_images": export_layer_images == True
            }

            if add_to_top:
                self.layer_data.insert(0, new_layer)
                # self.layer_thumbnails.insert(0, thumb)
            else:
                self.layer_data.append(new_layer)
                # self.layer_thumbnails.append(thumb)

            # self.layer_thumbnails.append(thumb)

        
        if len(data):
            self.set_unsaved_changes(True)
            self.redraw_all_layer_cards()
            self.set_preview_button(True)

    # def get_layer_thumbnail(self, layer_index):
    def create_layer_thumbnail(self, layer_index):
        try:
            if self.layer_data[layer_index].get("search_image_path"):
                with Image.open(self.layer_data[layer_index].get("search_image_path")) as image:
                    # image.show()
                    # image.copy().thumbnail((64,64)).show()
                    # return image.copy().thumbnail((64, 64))

                    thumbnail = image.copy()
                thumbnail.thumbnail((64,64))

                # self.layer_data[layer_index].update({"thumbnail":thumbnail})
                self.layer_data[layer_index].update({"thumbnail":ImageTk.PhotoImage(thumbnail)})

                # return ImageTk.PhotoImage(thumbnail)
        except Exception as e:
            # print("invalid border image:",e)
            self.layer_data[layer_index].update({"thumbnail":None})

    def search_type_option_selected(self, selected_option, set_unsaved_changes = True):
        self.search_type_subframes[self.search_types.index(selected_option)].lift()

        if selected_option == "Border":
            self.add_border_layer() # TODO This should ONLY run if something has actually changed
        else:
            border_index = next((i for i, layer in enumerate(self.layer_data) if layer["is_border"]), None)
            if border_index != None: self.delete_layer(border_index)
            
        if set_unsaved_changes: # hackey solution to making this not run upon creating new menu.
            # I'd prefer to have this ONLY if something's actually changed.
            self.set_unsaved_changes(True)

    def add_border_layer(self):
        self.layer_data.append({
            "name": "border",
            "is_border": True,
            "is_cosmetic_only": False, # or true? i dont remember
            "search_image_path": None,
            "source_image_path": None
        })
        # self.layer_thumbnails.append(None)

        # self.set_unsaved_changes(True) # Doesn't need this, as the optionmenu changing is enough
        self.redraw_all_layer_cards()
        # scroll all the way down?



    # def add_border(self, path = None):
    #     if path == None:
    #         path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])

    #     if path:
    #         if self.border_image != None:
    #             self.border_image.close()

    #         temp_border_image = Image.open(path)

    #         if len(self.layer_data):
    #             if self.layer_data[0]["img"].size != temp_border_image.size:
    #                 temp_border_image.close()
    #                 messagebox.showwarning("Warning", "The border must be the same size as the images")
    #                 return
            
    #         self.border_image = temp_border_image

    #         self.border_path = path
    #         self.border_label.config(text=os.path.basename(path))
    #         # self.update_preview()
    #         self.update_preview_button.configure(bg="#ffff00", fg="#000000")

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
                        # self.set_preset_pose_data(json.load(preset_json))["pose_data"] # i think i WANT the unsafe version; it'll throw an error if that doesnt exist, which is kinda what i want
                        # self.preset_pose_data = json.load(preset_pose_json)["pose_data"] # i think i WANT the unsafe version; it'll throw an error if that doesnt exist, which is kinda what i want
                        preset_data = json.load(preset_json)
                    self.set_preset_pose_data(preset_data["pose_data"])
                except json.JSONDecodeError as e:
                    pass # print exception: json invalid
                # other exceptions
    
    def set_preset_pose_data(self, preset_pose_data):
        # self.preset_pose_data = preset_pose_data["pose_data"] # i think i WANT the unsafe version; it'll throw an error if that doesnt exist, which is kinda what i want
        self.preset_pose_data = preset_pose_data
        self.preset_load_label.config(text=f"Pose data loaded as preset.\nPoses: {len(self.preset_pose_data)}")

    def move_image(self, index, direction):
        new_index = index + direction
        
        if 0 <= new_index < len(self.layer_data):
            
            self.layer_data[index], self.layer_data[new_index] = self.layer_data[new_index], self.layer_data[index]
            # self.layer_thumbnails[index], self.layer_thumbnails[new_index] = self.layer_thumbnails[new_index], self.layer_thumbnails[index]

            # self.redraw_layer_cards()
            
            self.redraw_layer_card(index)
            self.redraw_layer_card(new_index)

            # self.update_preview()
            # self.update_preview_button.configure(bg="#ffff00", fg="#000000")
            self.set_unsaved_changes(True)
            self.set_preview_button(True)

    def delete_layer(self, layer_index):
        had_search_image = self.layer_data[layer_index].get("search_image_path") != None

        del self.layer_data[layer_index]
        self.set_unsaved_changes(True)

        # could theoretically just do all layer cards *after* the deleted index, but also .redraw_all_layer_cards() has the necessary delete functionality
        self.redraw_all_layer_cards()

        if had_search_image: self.set_preview_button(True) # probably only set this if HAD a search image

    def redraw_layer_card(self, layer_index):
        # If card frame doesn't exist, create a new one. If it does, might as well use the existing one so we don't have to worry about re-ordering everything.
        card_frame = None
        if layer_index >= len(self.scrollable_frame.winfo_children()):
            card_frame = tk.Frame(self.scrollable_frame, bg=gui_shared.secondary_bg, highlightthickness=1, highlightbackground=gui_shared.secondary_fg, pady=0)
            # card_frame.pack(side="top", fill="x", expand=True, pady=2, padx=10)
            card_frame.pack(side="top", fill="x", expand=True, padx=10)
        else:
            card_frame = self.scrollable_frame.winfo_children()[layer_index]
            card_frame.configure(width=0)
            card_frame.pack_propagate(True)

            # Destroy all existing widgets.
            for widget in card_frame.winfo_children():
                widget.destroy()
        
        # presumably, these do not work because I'm trying to configure() that which was set in pack(), which will not work.
        # fiddle around with this
        # pad_top = 10 if (layer_index == 0) else 5
        # pad_bottom = 10 if (layer_index >= len(self.layer_data)) else 5
        # pad = [pad_top, pad_bottom]

        # card_frame.configure(pady=(pad_top, pad_bottom))
        # card_frame.configure(pady=pad)

        # card_frame.update()
        # card_frame.configure(pady=((10 if (layer_index == 0) else 5), (10 if (layer_index >= len(self.layer_data)) else 5)))
        # card_frame.pack_configure(pady=((10 if (layer_index == 0) else 5), (10 if (layer_index >= len(self.layer_data)) else 5)))
        card_frame.pack_configure(pady=((10 if (layer_index == 0) else 0), 10))
        # card_frame.update()

        # Get this layer's data, for convenience
        data = self.layer_data[layer_index]

        # Lots of things are formatted differently based on chosen settings 
        is_border = data.get("is_border") == True
        is_cosmetic_only = data.get("is_cosmetic_only") == True

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

        if data.get("search_image_path") and not ("thumbnail" in data): # If a thumbnail could exist and does not, create it
            self.create_layer_thumbnail(layer_index)

        # Place thumbnail. (I eventually want a checkerboard background for better visibility, but I don't know if it would actually help since the imgs are so small)
        tk.Label(content_left_frame, image=data.get("thumbnail"), bg=gui_shared.field_bg).pack(side="top", fill="both", expand=True, padx=10, pady=10)
        # thumbnail_label = tk.Label(content_left_frame, image=data.get("thumbnail"), bg=gui_shared.field_bg)
        # thumbnail_label.pack_propagate(False)
        # thumbnail_label.configure(height=thumbnail_label.winfo_width())
        # thumbnail_label.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        # Contains the entries, plus their respective buttons and labels
        content_right_frame = tk.Frame(content_top_frame, bg=gui_shared.secondary_bg, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        content_right_frame.pack(side="right", fill="both", expand=True)

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

        # Will this run every time the entry is UNFOCUSED, or every time ANYTHING IS TYPED? if it's the latter, it's quite annoying, but also who is gonna type these things anyway
        def save_search_image(e = None, entry=data, entry_widget=search_entry, i=layer_index):
            new_image_path = entry_widget.get()
            # if self.check_image_valid(new_image_path): # Check that image is the proper size, and that it is a valid image according to Pillow (I think)
            #     entry.update({"search_image_path":new_image_path})
                
            #     self.create_layer_thumbnail(i) # Force a thumbnail update
            #     self.redraw_layer_card(i) # Only need to redraw THIS card

            #     self.set_preview_button(True)
            #     self.set_unsaved_changes(True)
            entry.update({"search_image_path":new_image_path})
                
            self.create_layer_thumbnail(i) # Force a thumbnail update
            self.redraw_layer_card(i) # Only need to redraw THIS card

            self.set_preview_button(True)
            self.set_unsaved_changes(True)

        search_entry.bind("<FocusOut>", save_search_image, add="+")

        def pick_search_image(entry=data, entry_widget=search_entry):
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filedialog.askopenfilename(filetypes=[("Image File", "*.png;*.jpg;*.jpeg")]))
            # entry_widget.xview("end")
            save_search_image(entry=entry, entry_widget=entry_widget)
            
        search_button = tk.Button(search_frame, text="📁", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=pick_search_image)
        # search_button.pack(side="left", padx=(10,0), pady=((0 if is_border else 10),(10 if (is_cosmetic_only and not is_border) else 0)))
        search_button.pack(side="left", padx=(10,0))
        ToolTip(search_button, "Open a file dialog and select this layer's image, which will be searched for poses.")
            
        if not is_border and not is_cosmetic_only: # TODO: make source image disabled if search image entry is empty? idk
            source_frame = tk.Frame(content_right_frame, bg=gui_shared.secondary_bg)
            source_frame.pack(side="top", fill="x", padx=10, pady=(0,10))

            tk.Label(source_frame, text="Source img:", bg=gui_shared.secondary_bg, fg=gui_shared.fg_color).pack(side="left", padx=(0,5))

            source_entry = add_widget(tk.Entry, source_frame, {'width':1}, {'text':"""(OPTIONAL!) The search image is used to find identical copies, but the source image is used for the actual image output. If no source image is selected, the search image will be used instead.\n\n(Just leave this empty if you're not sure.)"""})
            source_entry.pack(side="left", fill="x", expand=True)
            
            if data.get("source_image_path"):
                source_entry.insert(0, data.get("source_image_path"))

            def save_source_image(e = None, entry=data, entry_widget=source_entry):
                new_image_path = entry_widget.get()
                # if self.check_image_valid(new_image_path):
                #     entry.update({"source_image_path":new_image_path})
                #     self.set_unsaved_changes(True)
                entry.update({"source_image_path":new_image_path})
                self.set_unsaved_changes(True)

            source_entry.bind("<FocusOut>", save_source_image, add="+")

            def pick_source_image(entry=data, entry_widget=source_entry):
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, filedialog.askopenfilename(filetypes=[("Image File", "*.png;*.jpg;*.jpeg")]))
                # entry_widget.xview("end")
                save_source_image(entry=entry, entry_widget=entry_widget)
                
            source_button = tk.Button(source_frame, text="📁", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=pick_source_image)
            # source_button.pack(side="left", padx=(10,0), pady=(0,10))
            source_button.pack(side="left", padx=(10,0))
            ToolTip(source_button, "(OPTIONAL!) The search image is used to find identical copies, but the source image is used for the actual image output. If no source image is selected, the search image will be used instead.\n\n(Just leave this alone if you're not sure.)")

            
        right_frame = tk.Frame(card_frame, bg=gui_shared.secondary_bg, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        right_frame.pack(side="right", fill="y")

        if not is_border:
            x_button = tk.Button(right_frame, width=2, text="X", fg=gui_shared.danger_fg, command=lambda idx=layer_index: self.delete_layer(idx), bg=gui_shared.button_bg)
            x_button.pack(side="top", padx=10, pady=(10,0))
            ToolTip(x_button, f"Delete layer {layer_index+1}")

        down_button = tk.Button(right_frame, width=2, text="↓", command=lambda idx=layer_index: self.move_image(idx, 1), bg=gui_shared.button_bg, fg=gui_shared.fg_color)

        down_button.pack(side="bottom", padx=10, pady=(0,10))
        ToolTip(down_button, "Reorder " + ("border" if is_border else f"layer {layer_index+1}") + " downwards")

        up_button = tk.Button(right_frame, width=2, text="↑", command=lambda idx=layer_index: self.move_image(idx, -1), bg=gui_shared.button_bg, fg=gui_shared.fg_color)
        up_button.pack(side="bottom", padx=10, pady=(10,0))
        ToolTip(up_button, "Reorder " + ("border" if is_border else f"layer {layer_index+1}") + " upwards")

        if not is_border:
            footer = tk.Frame(content_frame, bg=gui_shared.secondary_bg, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
            footer.pack(side="bottom", fill="both")

            cosmetic_checkbutton = tk.Checkbutton(footer, text="Cosmetic only", bg=gui_shared.secondary_bg, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False)
            cosmetic_checkbutton.pack(side="left", padx=10, pady=5)
            if is_cosmetic_only: cosmetic_checkbutton.select()
            ToolTip(cosmetic_checkbutton, "If selected, this layer will not be searched for pose images. Instead, the provided image will be exported alongside the pose images.")

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

            def save_export_check(entry=data):
                entry.update({"export_layer_images": entry.get("export_layer_images") != True})
                self.set_unsaved_changes(True)
                
            export_checkbutton.configure(command=save_export_check)
        else:
            data["is_cosmetic_only"] = True
            data["export_layer_images"] = True
            
        # card_frame.update()
        # # content_right_frame.update()
        # card_height = card_frame.winfo_height() # DEFINITELY put these in their own function - NO REASON to have this ONLY happen when cards are recreated entirely, we can just change width of existing cards without recreating them
        # # content_right_frame_width = content_right_frame.winfo_width()
        # card_frame.pack_propagate(False)
        # # content_right_frame.pack_propagate(False)
        # card_frame.configure(width=self.scrollable_frame.cget('width') - 18, height=card_height) # need to calibrate width such that padding and scrollbar is kept in mind. COULD definitely do something like the height, and only .pack() stuff with card_frame as master at the very end? but you'd need to do smth like, "save the width, then after everything's packed you can save the height and THEN turn off pack_propagate"
        # # content_right_frame.configure(width=content_right_frame_width)
        # card_frame.update()
        # # content_right_frame.update()

        self.update_layer_card_width(layer_index)

        gui_shared.bind_event_to_all_children(card_frame, "<MouseWheel>", self.on_left_frame_mousewheel)
        gui_shared.bind_event_to_all_children(card_frame, "<Button-1>", gui_shared.on_global_click)

    def redraw_all_layer_cards(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for i in range(len(self.layer_data)):
            self.redraw_layer_card(i)

    def update_layer_card_width(self, layer_index):
        # card_frame = None
        if layer_index >= len(self.scrollable_frame.winfo_children()):
            # card_frame = tk.Frame(self.scrollable_frame, bg=gui_shared.secondary_bg, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
            # card_frame.pack(side="top", fill="x", expand=True, pady=2, padx=10)
            return # idk PROBABLY raise exception? idk!!!
        else:
            # get card
            card_frame = self.scrollable_frame.winfo_children()[layer_index]

            # reset card size to what it wants to be automatically
            card_frame.configure(width=0)
            card_frame.pack_propagate(True)
            card_frame.update()
            
            card_height = card_frame.winfo_height() # get automatically-sized height
            card_frame.pack_propagate(False) # stop using automatic size
            card_frame.configure(width=self.scrollable_frame.cget('width') - 18, height=card_height) # need to calibrate width such that padding and scrollbar is kept in mind. COULD definitely do something like the height, and only .pack() stuff with card_frame as master at the very end? but you'd need to do smth like, "save the width, then after everything's packed you can save the height and THEN turn off pack_propagate"
            card_frame.update()


    def set_preview_button(self, can_update = True):
        # new_config = ({'bg':gui_shared.warning_bg, 'fg':gui_shared.warning_fg} if can_update else {'bg':gui_shared.button_bg, 'fg':gui_shared.fg_color})
        # self.update_preview_button.configure(*new_config)
        # new_config = ({'bg':gui_shared.warning_bg, 'fg':gui_shared.warning_fg} if can_update else {'bg':gui_shared.button_bg, 'fg':gui_shared.fg_color})
        self.update_preview_button.configure(
            bg=(gui_shared.warning_bg if can_update else gui_shared.button_bg), fg=(gui_shared.warning_fg if can_update else gui_shared.fg_color)
        )

    def update_preview_image(self):
        # print("got to update_preview_image")
        # self.update_preview_button.configure(bg=gui_shared.button_bg, fg=gui_shared.fg_color)
        self.set_preview_button(False)

        # composite = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        # def paste_center(base, img):
        #     img_ratio = min(width / img.width, height / img.height)
        #     new_size = (int(img.width * img_ratio), int(img.height * img_ratio))
            
        #     # zoomed_size = (int(img.width * self.zoom_level), int(img.height * self.zoom_level))
        #     # resized = img.resize(zoomed_size, Image.Resampling.LANCZOS)

        #     resized = img.resize(new_size, Image.Resampling.LANCZOS)

        #     offset = ((width - new_size[0]) // 2, (height - new_size[1]) // 2)
        #     base.paste(resized, offset, resized if resized.mode == 'RGBA' else None)

        # need a separate func for: pasting layers together into single preview image; displaying preview image

        if self.image_size == None:
            self.force_get_image_size()

        if self.image_size != None:
            # print(self.image_size)
            self.preview_image = Image.new("RGBA", self.image_size, ImageColor.getrgb(gui_shared.field_bg))
        else:
            print("Got to preview image creation with an image size of None, somehow")
            # raise ValueError
            return

        if not (gui_shared.warn_image_sizes(["Search image", "Source image"],
            [
                [layer.get("search_image_path") for layer in self.layer_data],
                [layer.get("source_image_path") for layer in self.layer_data]
            ]
        )): return

        for layer in reversed(self.layer_data):
            if layer.get("search_image_path"):
                with Image.open(layer["search_image_path"]) as image:
                    self.preview_image.alpha_composite(image)
        
        # print("gothere1")
        # print("Image size:", self.preview_image.size, "mode:", self.preview_image.mode)
        # self.formatted_canvas_image = ImageTk.PhotoImage(self.preview_image.convert("RGB"))

        # print("gothere2")

        # self.preview_canvas.delete("all")
        # self.img_id = self.preview_canvas.create_image(
        #     self.preview_canvas.winfo_width() // 2, self.preview_canvas.winfo_height() // 2, image=self.formatted_canvas_image, anchor="center")
        
        # print("gothere3")

        # if self.border_image:
        #     paste_center(composite, self.border_image)
        # for layer in reversed(self.layer_data):
        #     if layer.get("search_image_path"):
        #         with Image.open(layer["search_image_path"]) as image:
        #             paste_center(composite, image)

        # self.preview_canvas.delete("all")
        # self.preview_image = ImageTk.PhotoImage(composite)
        # self.preview_canvas.create_image(width // 2, height // 2, image=self.preview_image)

        # print("gothere4")
        
        # self.display_preview_image()

        # self.preview_viewportcanvas.set_image(self.formatted_canvas_image)
        self.preview_viewportcanvas.set_image(self.preview_image)

    #     # print("end of update preview image")


    # # def on_preview_canvas_mousewheel(self, event):
    # #     pass
    #     # delta = (event.delta // 120)
    #     # self.preview_canvas_zoom(delta, event.x, event.y)

    # # def preview_canvas_zoom(self, delta, x, y):
    # def preview_canvas_zoom(self, delta):
    #     # self.display_preview_image(delta)
    #     # self.display_preview_image((self.preview_zoom + (float(delta) / 10)) / self.preview_zoom)

    #     # old_zoom = self.preview_zoom
    #     # self.preview_zoom += (float(delta) / 10)

    #     # zoom_amount = 0.25 * self.preview_zoom

    #     # self.preview_zoom += zoom_amount * delta
    #     # self.preview_zoom = max(0.25, self.preview_zoom)
    #     # print(self.preview_zoom)
    #     # ok rather than this mathematical approach, we should do hard-coded step values
    #     steps = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 6.0] # SWITCH TO VIEWPORT METHOD WHATEVER THINGY

    #     if delta > 0 and self.preview_zoom != 10.0:
    #         self.preview_zoom = steps[steps.index(self.preview_zoom) + 1]
    #     elif delta < 0 and self.preview_zoom != .25:
    #         self.preview_zoom = steps[steps.index(self.preview_zoom) - 1]

    #     # factor = (self.preview_zoom + (float(delta) / 10)) / self.preview_zoom
    #     # factor = self.preview_zoom / old_zoom

    #     # self.preview_zoom += 

    #     # canvasx = self.preview_canvas.canvasx(x)
    #     # canvasy = self.preview_canvas.canvasy(y)
    #     # self.preview_canvas.scale("all", canvasx, canvasy, factor, factor)
    #     # self.display_preview_image(factor, canvasx, canvasy)
    #     # self.display_preview_image(canvasx, canvasy, self.preview_zoom)
    #     self.display_preview_image(self.preview_zoom)


    # # def display_preview_image(self, factor = 1.0, x = 0, y = 0):
    # # def display_preview_image(self, x = 0, y = 0, scale = 1.0):
    # def display_preview_image(self, scale = 1.0):
    #     if self.preview_image != None:
    #         # size = (int(self.preview_image.size[0] * scale), int(self.preview_image.size[1] * scale))
    #         self.formatted_canvas_image = ImageTk.PhotoImage(
    #             self.preview_image.convert("RGB").resize(
    #                 (int(self.preview_image.size[0] * scale), int(self.preview_image.size[1] * scale)), Image.Resampling.NEAREST
    #             )
    #         )
            
    #         # self.preview_canvas.delete("all")
            
    #         # self.preview_canvas.create_image(
    #         #     self.preview_canvas.winfo_width() // 2, self.preview_canvas.winfo_height() // 2, image=self.formatted_canvas_image, anchor="center")
            
    #         for widget in self.preview_contents_frame.winfo_children():
    #             widget.destroy()

    #         test = tk.Label(self.preview_contents_frame, image = self.formatted_canvas_image, bg=gui_shared.bg_color)
    #         test.pack(anchor="center")

    #         # self.preview_canvas.create_window(0,0,anchor="center",window=test)

    #         # self.preview_canvas.scale(self.img_id, x, y, 1, 1)
    #         # self.preview_canvas.scale(self.img_id, x, y, factor, factor)

    # def display_preview_image(self):
    #     pass

    # # def change_zoom(self, factor):
    # #     self.zoom_level *= factor
    # #     self.update_preview()

    def format_layer_json(self, paths_are_local = False):
        # name = self.name_entry_input.get()
        # if not name:
            # name = "unnamed_sprite_sheet"
        name = self.name_entry_input.get() or "unnamed_sprite_sheet"

        header = {
            "name": name,
            "consistxels_version": consistxels_version,
            "paths_are_local": paths_are_local,
            # "width": None,
            # "height": None
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

        pose_data = None

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
            # try: # NO, use try/except in relevant functions so they can stop or continue accordingly
            search_type_data.update({
                "border_color": None,
                "spacing_rows": int(self.spacing_rows.get()),
                "spacing_columns": int(self.spacing_columns.get()),
                "spacing_outer_padding": int(self.spacing_outer_padding.get()),
                "spacing_inner_padding": int(self.spacing_inner_padding.get()),
                "spacing_x_separation": int(self.spacing_x_separation.get()),
                "spacing_y_separation": int(self.spacing_y_separation.get())
            })
            # except:
            #     pass
        # elif padding, save pose data!
        elif search_type == "Preset":
            pose_data = self.preset_pose_data
        
        generation_data = {
            "automatic_padding_type": self.automatic_padding_type_option.get(),
            "custom_padding_amount": int(self.custom_padding_amount.get()),
            "generate_empty_poses": self.generate_empty_poses.get()
        }

        layer_data = []
        for layer in self.layer_data:
            search_image_path = layer.get("search_image_path")
            if search_image_path and paths_are_local: search_image_path = (
                f"{layer.get('name') or 'unnamed_layer'}{'' if (layer.get('is_border') or layer.get('is_cosmetic_only')) else '_search'}_image.png"
            )
            elif search_image_path == "": search_image_path = None

            source_image_path = layer.get("source_image_path")
            if source_image_path and paths_are_local: source_image_path = f"{layer.get('name') or 'unnamed_layer'}_source_image.png"
            elif source_image_path == "": source_image_path = None

            layer_data.append({
                "name": layer.get("name"),
                "search_image_path": search_image_path,
                "source_image_path": source_image_path,
                "is_border": layer.get("is_border") == True,
                "is_cosmetic_only": layer.get("is_cosmetic_only") == True,
                "export_layer_images": layer.get("export_layer_images") == True
            })
        
        formatted_data = {
            "header": header,
            "search_data": search_data,
            "search_type_data": search_type_data,
            "generation_data": generation_data,
            "layer_data": layer_data
        }

        if pose_data:
            formatted_data.update({"pose_data": pose_data})

        if not paths_are_local:
            output_folder_path = self.output_folder_path.get()
            if output_folder_path and output_folder_path != "":
                formatted_data.update({"output_folder_path":output_folder_path})

        return formatted_data

    def export_layerselect_all(self):
        try:
            formatted_data = self.format_layer_json(True)
        except ValueError:
            messagebox.showwarning("Warning!", "Please ensure all text input boxes are filled out correctly.\nIf a number is required, don't enter anything else.")
            return
        except Exception as e:
            messagebox.showerror("Error", e)
            return

        # path = filedialog.askdirectory(title="Choose a folder to save to (preferably empty)")
        
        path = filedialog.askdirectory(title="Select an output folder (preferably empty)")
        if path and ((not os.listdir(path)) or gui_shared.warn_overwrite()):
        # if path:
            layer_data = formatted_data["layer_data"]
            for i in range(len(layer_data)):
                if self.layer_data[i].get("search_image_path"):
                    with Image.open(self.layer_data[i].get("search_image_path")) as search_image:
                        search_image.save(os.path.join(path, layer_data[i]["search_image_path"]))
                
                if self.layer_data[i].get("source_image_path"):
                    with Image.open(self.layer_data[i].get("source_image_path")) as source_image:
                        source_image.save(os.path.join(path, layer_data[i]["source_image_path"]))
            
            json_path = os.path.join(path, f"consistxels_layerselect_{formatted_data['header']['name']}.json")
            with open(json_path, 'w') as file:
                json.dump(formatted_data, file, indent=4)
            
            self.set_unsaved_changes(False)
            messagebox.showinfo("Success!", f".json file and all layer images exported")
            return True
        return False

    def export_layerselect_json(self):
        # name = self.name_entry_input.get()
        # if not name:
        #     name = "unnamed_sprite_sheet"
        try:
            formatted_data = self.format_layer_json(False)
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
    def import_layerselect_json(self, path = None):
        if not path: path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("Json File", "*.json")])
        if path:
            with open(path) as json_file:
                json_data = json.load(json_file)
                
            try:
                header = json_data.get("header")
                search_data = json_data.get("search_data")
                search_type_data = json_data.get("search_type_data")
                generation_data = json_data.get("generation_data")
                layer_data = json_data.get("layer_data")
                pose_data = json_data.get("pose_data")
                output_folder_path = json_data.get("output_folder_path")

                # header
                self.name_entry_input.set(header["name"])

                # in the future, if things are different between versions, do such checks and changes here
                paths_are_local = header["paths_are_local"]

                self.start_search_in_center.set(search_data.get("start_search_in_center"))
                self.search_right_to_left.set(search_data.get("search_right_to_left"))
                self.detect_identical_images.set(search_data.get("detect_identical_images"))
                self.detect_rotated_images.set(search_data.get("detect_rotated_images"))
                self.detect_flip_h_images.set(search_data.get("detect_flip_h_images"))
                self.detect_flip_v_images.set(search_data.get("detect_flip_v_images"))

                
                # self.search_types[self.search_types.index(search_type_data.get("search_type"))]

                # self.search_type_option.set(
                #     self.search_types[self.search_types.index(search_type_data.get("search_type"))] # HOPEFULLY this works???
                # )
                self.search_type_option.set(search_type_data["search_type"]) # this should work, actually
                self.search_type_option_selected(search_type_data["search_type"], False)

                if search_type_data["search_type"] == "Border":
                    self.update_border_color(self.format_color_string(search_type_data["border_color"]))
                elif search_type_data["search_type"] == "Spacing":
                    self.spacing_rows.set(str(search_type_data["spacing_rows"]))
                    self.spacing_columns.set(str(search_type_data["spacing_columns"]))
                    self.spacing_outer_padding.set(str(search_type_data["spacing_outer_padding"]))
                    self.spacing_inner_padding.set(str(search_type_data["spacing_inner_padding"]))
                    self.spacing_x_separation.set(str(search_type_data["spacing_x_separation"]))
                    self.spacing_y_separation.set(str(search_type_data["spacing_y_separation"]))
                # elif search_type_data["search_type"] == "Preset" and pose_data: # honestly, we dont NEED to do this if it's ONLY preset, right?
                    # self.pose_data = pose_data
                    # need to think of clever way to not allow textbox entry, but to show that it's been loaded regardless? idk TODO TODO TODO TODO TODO
                if pose_data:
                    self.set_preset_pose_data(pose_data)

                # self.add_border(header["border_path"])
                # if header["start_search_in_center"]:
                # self.search_right_to_left.set(header["search_right_to_left"])

                # if header["search_right_to_left"]:
                    # pass

                # self.automatic_padding_type_option.set(header["automatic_padding_type"])
                # self.automatic_padding_type_option.set(self.padding_types[generation_data.get("automatic_padding_type")])
                self.automatic_padding_type_option.set(generation_data.get("automatic_padding_type"))

                # self.custom_padding_amount.set(header["custom_padding_amount"])
                self.custom_padding_amount.set(generation_data["custom_padding_amount"])

                # delete current images too!!!
                # self.add_image_layers(layer_data)

                # delete any current layers
                for i in reversed(range(len(self.layer_data))):
                    # self.delete_layer(i)
                    del self.layer_data[i]
                
                # reformat layer paths if paths_are_local == True
                curr_folder_path = os.path.dirname(path) if paths_are_local else ""

                for layer in layer_data:

                        # if search_image_path:
                        #     layer["search_image_path"] = os.path.join(curr_folder_path,
                        #         f"{layer.get('name') or 'unnamed_layer'}{'' if (layer.get('is_border') or layer.get('is_cosmetic_only')) else '_search'}_image.png"
                        #     )
                    search_image_path = layer.get("search_image_path")
                    if search_image_path:
                        path = os.path.join(curr_folder_path, search_image_path)
                        # if self.check_image_valid(path):
                        #     layer["search_image_path"] = path
                        layer["search_image_path"] = path
                        
                    source_image_path = layer.get("source_image_path")
                    if source_image_path:
                        path = os.path.join(curr_folder_path, source_image_path)
                        # if self.check_image_valid(path):
                        #     layer["source_image_path"] = path
                        layer["source_image_path"] = path

                
                self.add_image_layers(layer_data)

                if output_folder_path: self.output_folder_path.set(output_folder_path)

                self.set_unsaved_changes(False)
            except json.JSONDecodeError as e:
                messagebox.showerror("Error importing .json", e) # not sure for what reason i'd need to have these separated, but i guess it's nice to catch 'em
            except Exception as e:
                messagebox.showerror("Error importing .json", e)

    def generate_button_pressed(self):
        size_check = gui_shared.warn_image_sizes(["Search image", "Source image"],
            [
                [layer.get("search_image_path") for layer in self.layer_data],
                [layer.get("source_image_path") for layer in self.layer_data]
            ]
        )

        data = self.format_layer_json(False)

        # check for output folder in entry, when I get around to adding it
        # TEMP_output_folder_path = filedialog.askdirectory(title="Select an output folder")
        output_folder_path = self.output_folder_path.get()

        # if len(layer_data) > 0 and header["name"] != "" and not duplicate_layer_name and output_folder_path:
        if data.get("layer_data") and (self.name_entry_input.get() and self.name_entry_input.get() != "") and output_folder_path and size_check:
            try:
                temp_json_data = {"data": data, "output_folder_path": output_folder_path}

                with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_json_file:
                    json.dump(temp_json_data, temp_json_file)
                    print(json.dumps({"type": "generate_pose_data", "val": temp_json_file.name.replace('\\', '/')}), flush=True)

            except Exception as e:
                print(json.dumps({"type": "error", "val": e}), flush=True)
        else:
            warning_output = ""

            # if self.border_path == None: warning_output += "Please add a border image"
            # if len(layer_data) <= 0:
            if not data.get("layer_data"):
                if warning_output != "": warning_output += "\n"
                warning_output += "Please add at least one layer"
            if not (self.name_entry_input.get() and self.name_entry_input.get() != ""):
                if warning_output != "": warning_output += "\n"
                warning_output += "Please enter a name for this sprite sheet"
            # if duplicate_layer_name: # do we NEED this???
            #     if warning_output != "": warning_output += "\n"
            #     warning_output += "Ensure all layers have unique names"
            if not output_folder_path:
                if warning_output != "": warning_output += "\n"
                warning_output += "You must select an output folder first"

            if warning_output:
                messagebox.showwarning("Wait!", warning_output)
    
    def update_progress(self, value, header_text, info_text):
        self.progress_bar["value"] = value
        self.progress_header_label.configure(text=header_text)
        self.progress_info_label.configure(text=info_text)
    
    def cancel_generate(self):
        print(json.dumps({"type": "cancel"}), flush=True)
    
    def generate_began(self):
        self.generate_button.configure(state="disabled")
        self.load_button.configure(state="disabled")
        self.clear_button.configure(state="disabled")
        self.back_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")

    def generate_ended(self):
        self.generate_button.configure(state="normal")
        self.load_button.configure(state="normal")
        self.clear_button.configure(state="normal")
        self.back_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")

        # Is this fine? It IS, right??? Like, the user WILL have the .json by now, so it's fine, right?????
        self.set_unsaved_changes(False)
    
    def set_unsaved_changes(self, new_unsaved_changes = True):
        self.back_button.config(fg=(gui_shared.danger_fg if new_unsaved_changes else gui_shared.fg_color))
        self.set_unsaved_changes_callback(new_unsaved_changes)

    def save_changes(self):
        return self.export_layerselect_json()
