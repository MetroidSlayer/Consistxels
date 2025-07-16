import json
import os
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
# from PIL import Image

import scripts.gui.gui_shared as gui_shared
from scripts.gui.gui_shared import add_widget
from scripts.classes.tooltip import ToolTip

UPDATE_INDIVIDUAL_AUTO = 0
UPDATE_INDIVIDUAL_MANUAL = 1
UPDATE_MULTILAYER_FILE = 2

EXPORT_SINGLE_MERGED = 0
EXPORT_INDIVIDUAL_LAYERS = 1
EXPORT_MULTILAYER_FILE = 2

POSE_ALL = 0
POSE_UNIQUE = 1
POSE_BOTH = 2

# Menu for exporting sprite sheets, layers, and pose images for already-generated sheet data
class Menu_ExportSheet(tk.Frame):
    def __init__(self, master, change_menu_callback, load_path = None): # TODO change load to only accept sheetdata_generated json type
        super().__init__(master) # Initialize menu's tkinter widget
        self.input_folder_path = None # Input folder path must be stored so images can be loaded later
        self.json_data = None
        self.image_size = None
        self.configure(bg=gui_shared.bg_color) # Change bg color
        self.after(0, self.setup_ui, change_menu_callback, load_path) # .setup_ui() in .after() to prevent ugly flickering
    
    # Setup UI
    def setup_ui(self, change_menu_callback, load_path = None):

        # Header
        # TODO: AT SOME POINT, make header and other common stuff part of a common menu class that the specific menus can inherit from
        self.header = tk.Frame(self, bg=gui_shared.bg_color)
        self.header.pack(fill="x", padx=2)

        # Header left:
        
        # Load button
        self.load_button = tk.Button(self.header, text="📁 Load", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=self.load_json)
        self.load_button.pack(padx=(12,10), pady=10, side="left")
        ToolTip(self.load_button, "Load a .json file containing sprite sheet data. Must be located in the same folder as its pose images.")

        # Header right:

        # Back button
        self.back_button = tk.Button(self.header, text="Back to Main Menu", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=lambda: change_menu_callback("Main"))
        self.back_button.pack(side="right", padx=10, pady=10)
        ToolTip(self.back_button, "...Come on, this one is self explanatory.", False, True, 2000)
        
        # Main frame
        self.main_frame = tk.Frame(self, bg=gui_shared.bg_color)
        self.main_frame.pack(fill="both", expand=True)

        # Menus inside paned window so they can be resized
        paned_window = tk.PanedWindow(self.main_frame, bg=gui_shared.bg_color, opaqueresize=False, sashrelief="flat", sashwidth=16, bd=0)
        paned_window.pack(fill="both", expand=True)

        # Left frame
        self.left_frame = tk.Frame(paned_window, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        self.left_frame.pack(side="left", fill="y", padx=10)
        self.left_frame.pack_propagate(False)

        # Right frame
        self.right_frame = tk.Frame(paned_window, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        self.right_frame.pack(side="right", fill="y", padx=10)
        self.right_frame.pack_propagate(False)

        # Add menus to paned window, define behavior
        paned_window.add(self.left_frame, minsize=400, stretch="always")
        paned_window.add(self.right_frame, minsize=400, stretch="always")

        # Layer list header
        layer_header = tk.Frame(self.left_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        layer_header.pack(side="top", fill="x")

        # Stored in self because it needs to change once something is loaded
        self.loaded_json_filename_label = tk.Label(layer_header, text="No .json loaded", bg=gui_shared.bg_color, fg=gui_shared.fg_color)
        self.loaded_json_filename_label.pack(padx=10, pady=10, anchor="w")

        self.loaded_json_sheetname_label = tk.Label(layer_header, text="", bg=gui_shared.bg_color, fg=gui_shared.fg_color)
        self.loaded_json_sheetname_label.pack(padx=10, anchor="w")

        tk.Label(layer_header, text="Layers:", bg=gui_shared.bg_color, fg=gui_shared.fg_color).pack(padx=10, pady=10, anchor="w")

        # Layer list
        layer_list_container_frame = tk.Frame(self.left_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        layer_list_container_frame.pack(side="top", fill="both", expand=True)

        self.layer_canvas_frame = tk.Frame(layer_list_container_frame, bg=gui_shared.bg_color, width=0)
        self.layer_canvas_frame.pack(side="left", fill="both", expand=True)
        
        self.layer_canvas = tk.Canvas(self.layer_canvas_frame, bg=gui_shared.bg_color, highlightthickness=0, width=0)

        self.layer_scrollbar = tk.Scrollbar(layer_list_container_frame, orient="vertical", command=self.layer_canvas.yview)
        self.layer_scrollbar.pack(side="left", fill="y", padx=(2,0), pady=0)

        self.scrollable_frame = tk.Frame(self.layer_canvas, bg=gui_shared.bg_color)

        # Bind scrolling
        self.scrollable_frame.bind("<Configure>", lambda e: self.layer_canvas.configure(scrollregion=self.layer_canvas.bbox("all")))

        # Create canvas in which to show layer info
        self.layer_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.layer_canvas.configure(yscrollcommand=self.layer_scrollbar.set)

        self.layer_list_frame = tk.Frame(self.scrollable_frame, bg=gui_shared.bg_color) # TODO Consider changing name: too similar to self.layer_frame_list
        self.layer_list_frame.pack(fill="both", expand=True)
        self.layer_list_frame.pack_propagate(False)
        
        self.layer_list_header_frame : tk.Frame = None # Frame holding options that effect all layers

        self.layer_frame_list : list[tk.Frame] = [] # Will contain frame widgets containing info and options for a given layer
        self.layer_update_list : list[tk.BooleanVar] = [] # Will contain tk.BooleanVar()s representing whether a given layer's pose images will be updated
        self.layer_export_list : list[tk.BooleanVar] = [] # Will contain tk.BooleanVar()s representing whether a given layer will be visible in export
        self.layer_path_list : list[tk.StringVar] = [] # Will contain tk.StringVar()s representing the paths to the image being used to update a given layer's poses

        self.layer_update_all : tk.BooleanVar = None # Will contain booleanvars for layer list header
        self.layer_export_all : tk.BooleanVar = None

        # For resizing the layer widgets so they fit in the canvas.
        def resize_layer_list(_ = None):
            self.layer_canvas_frame.update_idletasks()
            self.scrollable_frame.configure(width = self.layer_canvas_frame.winfo_width())
            
            self.resize_layer_list()
        
        self.left_frame.bind("<Configure>", resize_layer_list)

        self.layer_canvas.pack(side="left", fill="both", expand=True)

        # Bind mousewheel for scrolling left frame
        gui_shared.bind_event_to_all_children(self.left_frame,"<MouseWheel>",self.on_left_frame_mousewheel)

        # Export options

        update_options_frame = tk.Frame(self.right_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        update_options_frame.pack(fill="both", expand=True)

        # TODO make some options enable/disable if certain conditions are met / settings are selected

        # Update checkbutton

        self.updating = tk.BooleanVar()
        self.updating.set(True)
        self.update_checkbutton = tk.Checkbutton(update_options_frame, text=f"Update pose images",
            bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, variable=self.updating)
        self.update_checkbutton.pack(anchor="w", padx=10, pady=10)
        ToolTip(self.update_checkbutton, "If checked, the program will attempt to update the pose images.")

        # Update radio buttons

        tk.Label(update_options_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Update type:").pack(anchor="w", padx=10, pady=10)
        
        self.update_type = tk.IntVar()
        self.update_type.set(0)

        radio_update_individual_auto = tk.Radiobutton(update_options_frame, text="Update from individual images (auto)", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, variable=self.update_type, value=UPDATE_INDIVIDUAL_AUTO, command=self.redraw_layer_list_items)
        radio_update_individual_auto.pack(anchor="w", padx=10)
        ToolTip(radio_update_individual_auto, "The current folder will be searched for images that match the default name for an individual layer export, and if they are found, they'll be used to update the relevant pose images.")
        # TODO add a second part to tooltip that describes format being looked for

        radio_update_individual_manual = tk.Radiobutton(update_options_frame, text="Update from individual images (manual)", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, variable=self.update_type, value=UPDATE_INDIVIDUAL_MANUAL, command=self.redraw_layer_list_items)
        radio_update_individual_manual.pack(anchor="w", padx=10)
        ToolTip(radio_update_individual_manual, "You'll be able to manually input file paths to be used to update the relevant pose images. If a layer is not given a file path, its unique pose images will be unaffected.")

        radio_update_multilayer = tk.Radiobutton(update_options_frame, text="Update from multi-layered file", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, variable=self.update_type, value=UPDATE_MULTILAYER_FILE, command=self.redraw_layer_list_items)
        radio_update_multilayer.pack(anchor="w", padx=10)
        ToolTip(radio_update_multilayer, "Input a multi-layered file (.aseprite, .psd). If layers are found in the file that match the layers' names, they will be used to update the relevant pose images.")
        # TODO MAKE SURE THIS DESC FITS THE FILETYPE IM ACTUALLY SUPPORTING!!! TRY adding psd and gimp support

        def update_check_button_states():
            state = "normal" if self.updating.get() else "disabled"

            radio_update_individual_auto.config(state=state)
            radio_update_individual_manual.config(state=state)
            radio_update_multilayer.config(state=state)

            self.redraw_layer_list_items()

        self.update_checkbutton.config(command=update_check_button_states)

        self.update_multilayer_file_path = tk.StringVar() # By default, not attached to a widget, but it will be later once that entry shows up

        export_options_frame = tk.Frame(self.right_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        export_options_frame.pack(fill="both", expand=True)

        # Export checkbutton

        self.exporting = tk.BooleanVar()
        self.exporting.set(True)
        self.export_checkbutton = tk.Checkbutton(export_options_frame, text=f"Export sheet / layer(s)",
            bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, variable=self.exporting, command=self.redraw_layer_list_items)
        self.export_checkbutton.grid(padx=10, pady=10, row=0, column=0, sticky="W", columnspan=2)
        ToolTip(self.export_checkbutton, "If checked, the program will use the pose images to export full sprite sheet or layer images.")

        # Export radio buttons

        # tk.Label(export_options_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Export type:").pack(anchor="w", padx=10, pady=10)
        tk.Label(export_options_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Export type:").grid(padx=10, pady=10, row=1, column=0, sticky="W")

        # Stores radio button value
        # 0: single image, 1: individual layer image(s), 2: multi-layer file
        self.export_type = tk.IntVar()
        self.export_type.set(0)

        radio_export_single = tk.Radiobutton(export_options_frame, text="Single merged image", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, variable=self.export_type, value=EXPORT_SINGLE_MERGED)
        radio_export_single.grid(padx=10, row=2, column=0, sticky="W")
        ToolTip(radio_export_single, "Export one image containing all selected layers merged together.")

        radio_export_layers = tk.Radiobutton(export_options_frame, text="Individual layer image(s)", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, variable=self.export_type, value=EXPORT_INDIVIDUAL_LAYERS)
        radio_export_layers.grid(padx=10, row=3, column=0, sticky="W")
        ToolTip(radio_export_layers, "Export an image for each selected layer.")

        radio_export_multilayer = tk.Radiobutton(export_options_frame, text="Multi-layered file", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, variable=self.export_type, value=EXPORT_MULTILAYER_FILE)
        radio_export_multilayer.grid(padx=10, row=4, column=0, sticky="W")
        ToolTip(radio_export_multilayer, "Export one file that contains all images as layers.")

        # Pose type radio buttons

        tk.Label(export_options_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Pose images to export:").grid(padx=10, pady=10, row=1, column=1, sticky="W")

        self.pose_type = tk.IntVar()
        self.pose_type.set(0)

        radio_pose_all = tk.Radiobutton(export_options_frame, text="Use all", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, variable=self.pose_type, value=POSE_ALL)#, command=self.redraw_layer_list_items)
        radio_pose_all.grid(padx=10, row=2, column=1, sticky="W")
        ToolTip(radio_pose_all, "Every pose image within a pose will be shown. Intended for tests or final exports in which the sheet's used in context.")

        radio_pose_unique = tk.Radiobutton(export_options_frame, text="Use unique only", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, variable=self.pose_type, value=POSE_UNIQUE)#, command=self.redraw_layer_list_items)
        radio_pose_unique.grid(padx=10, row=3, column=1, sticky="W")
        ToolTip(radio_pose_unique, """Exported layers will only contain unique pose images. They'll be positioned where they were initially found during the "Generate Sprite Sheet Data" search, so they might be a little spread out.\n\nIn general, if you're transferring a number of poses from one sheet to another, this will be much faster than opening each pose image individually. After modifying unique-only layers, use the "Update pose images" export type to make sure individual pose images are up-to-date, then generate the whole sheet.\n\n(Does not work with the "Single merged image" or "Update pose images" export types.)""")

        radio_pose_both = tk.Radiobutton(export_options_frame, text="Both (multi-layer only)", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, variable=self.pose_type, value=POSE_BOTH, state="disabled")#, command=self.redraw_layer_list_items)
        radio_pose_both.grid(padx=10, row=4, column=1, sticky="W")
        ToolTip(radio_pose_both, "Both the complete layer and the unique-only layer will be provided in the file. (Only applies to the \"Multi-layered file\" export type.)")

        # File type selection optionmenu
        tk.Label(export_options_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Export file type:").grid(padx=10, pady=10, row=5, column=0, sticky="W", columnspan=2)

        self.image_file_types = [".png", ".jpg", ".bmp"] # Options for image filetypes
        self.multilayer_file_types = [".aseprite (Aseprite)", ".psd (PhotoShop, GIMP)"] # Options for multilayer filetypes

        self.file_type_option = tk.StringVar(value=self.image_file_types[0])
        self.file_type_optionmenu : tk.OptionMenu = None

        def create_file_type_optionmenu():
            if self.file_type_optionmenu != None:
               self.file_type_optionmenu.destroy() 
               self.file_type_optionmenu = None
            
            options = self.image_file_types if self.export_type.get() != EXPORT_MULTILAYER_FILE else self.multilayer_file_types
            
            if not self.file_type_option.get() in options:
                self.file_type_option.set(options[0])

            self.file_type_optionmenu = tk.OptionMenu(export_options_frame, self.file_type_option, *options)
            self.file_type_optionmenu.configure(bg=gui_shared.field_bg, fg=gui_shared.fg_color, activebackground=gui_shared.bg_color, activeforeground=gui_shared.fg_color, width=28, anchor="w", justify="left", highlightthickness=1, highlightbackground=gui_shared.secondary_fg, bd=0, relief="flat")
            self.file_type_optionmenu["menu"].configure(bg=gui_shared.field_bg, fg=gui_shared.fg_color, activebackground=gui_shared.secondary_bg, activeforeground=gui_shared.fg_color, relief="solid")
            self.file_type_optionmenu.grid(padx=10, pady=(0,10), row=6, column=0, sticky="EW", columnspan=2)

        create_file_type_optionmenu()

        def export_check_button_states():
            exporting = self.exporting.get()
            state = "normal" if exporting else "disabled"

            radio_export_single.config(state=state)
            radio_export_layers.config(state=state)
            radio_export_multilayer.config(state=state)

            radio_pose_all.config(state=state)
            radio_pose_unique.config(state=state)
            radio_pose_both.config(state=state)

            if self.file_type_optionmenu != None:
                self.file_type_optionmenu.config(state=state)

            if exporting:
                if self.export_type.get() == EXPORT_MULTILAYER_FILE:
                    
                    if not self.file_type_option.get() in self.multilayer_file_types:
                        create_file_type_optionmenu()
                        self.file_type_option.set(self.multilayer_file_types[0])
                else:
                    radio_pose_both.config(state="disabled")

                    if self.pose_type.get() == POSE_BOTH:
                        self.pose_type.set(0)
                    
                    if not self.file_type_option.get() in self.image_file_types:
                        create_file_type_optionmenu()
                        self.file_type_option.set(self.image_file_types[0])
        
        def export_check_button_states_and_redraw():
            export_check_button_states()
            self.redraw_layer_list_items()

        self.export_checkbutton.config(command=export_check_button_states_and_redraw)
        radio_export_single.config(command=export_check_button_states)
        radio_export_layers.config(command=export_check_button_states)
        radio_export_multilayer.config(command=export_check_button_states)

        output_path_frame = tk.Frame(self.right_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        output_path_frame.pack(fill="both", expand=True, anchor="s")

        tk.Label(output_path_frame, text="Output folder path:", bg=gui_shared.bg_color, fg=gui_shared.fg_color).pack(side="left", padx=(10,5), pady=10)

        self.output_folder_path = tk.StringVar()
        self.output_folder_entry = add_widget(tk.Entry, output_path_frame, {'width':1, 'textvariable':self.output_folder_path, 'disabledbackground':gui_shared.secondary_bg}, {'text':"""Enter the path to the folder where the exported images will be output.\n\n(It's recommended that you choose a new, EMPTY folder! Choosing an existing one will clutter up your files at best, and overwrite existing data at worst. That said, if you WANT to overwrite existing data, go for it.)"""})
        self.output_folder_entry.pack(side="left", fill="x", expand=True, pady=10)

        # Open file dialog for output folder path
        def select_output_folder_path(use_input_path = False):
            if not use_input_path:
                path = filedialog.askdirectory(title="Select an output folder (preferably empty)")
            else:
                path = self.input_folder_path
            
            if (path and ((not os.listdir(path)) or gui_shared.warn_overwrite())):
                self.output_folder_path.set(path)

                self.check_reset_progress()

        self.output_folder_button = tk.Button(output_path_frame, text="📁", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=select_output_folder_path)
        self.output_folder_button.pack(side="left", padx=10, pady=10)
        ToolTip(self.output_folder_button, """Open a file dialog and select the folder where the exported images will be output.\n\n(It's recommended that you choose a new, EMPTY folder! Choosing an existing one will clutter up your files at best, and overwrite existing data at worst. That said, if you WANT to overwrite existing data, go for it.)""")

        self.output_use_current_folder_button = tk.Button(output_path_frame, text="Use current folder", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=lambda p=True: select_output_folder_path(p))
        self.output_use_current_folder_button.pack(side="left", padx=(0,10), pady=10)
        ToolTip(self.output_use_current_folder_button, """Select this .json's folder as the output folder.\n\n(Recommended. Keep in mind that you might still overwrite previous exports, but you're very unlikely to overwrite any pose images.)""")

        # Progress bar, confirmation/cancellation buttons
        
        export_container_frame = tk.Frame(self.right_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        export_container_frame.pack(side="bottom", fill="x")

        export_buttons_frame = tk.Frame(export_container_frame, bg=gui_shared.bg_color)
        export_buttons_frame.pack(side="left")

        self.export_button = tk.Button(export_buttons_frame, text="Export...", command=self.generate_button_pressed, bg=gui_shared.button_bg, fg=gui_shared.fg_color, state="disabled")
        self.export_button.pack(side="top", padx=10, pady=10)
        ToolTip(self.export_button, "Export or update images based on selected options.", True)

        self.cancel_button = tk.Button(export_buttons_frame, text="Cancel", command=self.cancel_generate, fg=gui_shared.danger_fg, bg=gui_shared.button_bg, state="disabled")
        self.cancel_button.pack(side="top", padx=10, pady=(0,10), fill="x")
        ToolTip(self.cancel_button, "Cancel export", True)

        generate_progress_frame = tk.Frame(export_container_frame, bg=gui_shared.bg_color)
        generate_progress_frame.pack(side="left", fill="x", expand=True)

        self.progress_header_label = tk.Label(generate_progress_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color)
        self.progress_header_label.pack(side="top", padx=(0,10), pady=(10,0), fill="x", expand=True)

        self.progress_info_label = tk.Label(generate_progress_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color)
        self.progress_info_label.pack(side="top", padx=(0,10), pady=(0,5), fill="x", expand=True)
        
        self.progress_bar = ttk.Progressbar(generate_progress_frame, orient="horizontal", maximum=100)
        self.progress_bar.pack(padx=(0,10), pady=(0,10), side="top", fill="x", expand=True)
        
        # If a path was passed when the menu was created, open that path
        if load_path: self.load_json(load_path)

    # Initial draw of layer list, which contains options and such. Call this upon new .json loaded, not upon option change.
    def draw_layer_list(self):
        # Destroy current layer list
        for widget in self.layer_frame_list:
            widget.destroy()
        
        # Header, which contains options that effect all layers
        self.layer_list_header_frame = tk.Frame(self.layer_list_frame, bg=gui_shared.button_bg)
        self.layer_list_header_frame.pack(anchor="w", fill="x")
        self.layer_list_header_frame.grid_columnconfigure(2, weight=1)
        self.redraw_layer_list_header() # Add options
        
        # Reset stored vals for previous layers
        self.layer_update_list = []
        self.layer_export_list = []
        self.layer_path_list = []

        left_frame = tk.Frame(self.layer_list_frame, bg=gui_shared.bg_color)
        left_frame.pack(side="left", fill="both")
        right_frame = tk.Frame(self.layer_list_frame, bg=gui_shared.bg_color)
        right_frame.pack(side="left", fill="both", expand=True)

        right_frame.columnconfigure(0, weight=1)

        for i, layer in enumerate(self.json_data["layer_data"]):
            left_frame.rowconfigure(i, weight=1)

            bg_color = gui_shared.secondary_bg if i % 2 else gui_shared.bg_color

            label_frame = tk.Frame(left_frame, bg=bg_color)
            label_frame.grid(row=i, column=0, sticky="NSEW")
            label_frame.grid_anchor("w")

            tk.Label(label_frame, bg=bg_color, fg=gui_shared.fg_color, text=f"{i + 1}: {layer.get('name', '(unnamed layer)')}{' (cosmetic)' if layer.get('is_cosmetic_only') else ''}").grid(row=0, column=0, sticky="W", padx=10, pady=10)

            contents = tk.Frame(right_frame, bg=bg_color)
            contents.grid(row=i, column=0, sticky="NSEW")
            contents.grid_columnconfigure(2, weight=1)
            self.layer_frame_list.append(contents)

            # tk.BooleanVars for tracking if layers should update/export
            self.layer_update_list.append(None if layer.get('is_cosmetic_only') else tk.BooleanVar(value=True))
            self.layer_export_list.append(tk.BooleanVar(value=True))
            self.layer_path_list.append(tk.StringVar)

            self.redraw_layer_list_item(i)

    # Secondary draw of the header entry in the visible layer list, which has options that effect all layers
    # TODO for this, and for the individual list items, no reason to redraw if nothing's changed. so make sure only relevant options actually redraw, and try to find a way to prevent redraws if everything will end up being the same
    def redraw_layer_list_header(self):
        # Destroy existing widgets
        for widget in self.layer_list_header_frame.winfo_children():
            widget.destroy()

        update_checkbutton = None
        export_checkbutton = None
        update_entry_frame = None

        # Update checkbutton will only appear if the user is updating the layers, and if it's a normal (i.e. non-cosmetic/border) layer
        if self.updating.get():
            
            self.layer_update_all = tk.BooleanVar(value=True)
            
            def update_set_all():
                for var in self.layer_update_list:
                    if var != None: var.set(self.layer_update_all.get())
            
            update_checkbutton = tk.Checkbutton(self.layer_list_header_frame, text=f"Update all",
                bg=gui_shared.button_bg, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg,
                onvalue=True, offvalue=False, variable=self.layer_update_all, command=update_set_all)
            
            ToolTip(update_checkbutton, "If checked, the program will update this layer's unique pose images according to the option selected on the right.")

            # Label, entry, and button for selecting filepath. Will only appear if the user is updating pose images w/ a multilayer file.
            if self.update_type.get() == UPDATE_MULTILAYER_FILE:
                update_entry_frame = tk.Frame(self.layer_list_header_frame, bg=gui_shared.button_bg)

                tk.Label(update_entry_frame, bg=gui_shared.button_bg, fg=gui_shared.fg_color, text="Multi-layered file:").pack(side="left", padx=(10,5), pady=10)
                
                entry = add_widget(tk.Entry, update_entry_frame, {"textvariable": self.update_multilayer_file_path, "width": 1}, {"text": "Enter the path to the multi-layered file you want to use to update this layer's pose images."})
                entry.pack(side="left", fill="x", expand=True, pady=10)

                button = tk.Button(update_entry_frame, bg=gui_shared.button_bg, fg=gui_shared.fg_color, text="📁",
                    command=lambda s=self.update_multilayer_file_path, f=[("Multi-layered files", "*.ase; *.aseprite; *.psd")]: gui_shared.ask_open_file_for_stringvar(s,f)) # TODO make sure supported filetypes are all here
                button.pack(side="left", padx=10, pady=10)
                ToolTip(button, "Select the multi-layered file you want to use to update this layer's pose images.")

        # Export checkbutton if the user is exporting the layers
        if self.exporting.get():
            
            self.layer_export_all = tk.BooleanVar(value=True)
            
            def export_set_all(): # If this is checked or unchecked, do the same to all other checkbuttons
                for var in self.layer_export_list:
                    if var != None: var.set(self.layer_export_all.get())
            
            export_checkbutton = tk.Checkbutton(self.layer_list_header_frame, text=f"Export all",
                bg=gui_shared.button_bg, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg,
                onvalue=True, offvalue=False, variable=self.layer_export_all, command=export_set_all)

            ToolTip(export_checkbutton, "If checked, the program will include this layer in the export according to the option selected on the right.")
        
        if update_checkbutton and self.update_type.get() != UPDATE_INDIVIDUAL_MANUAL: # If manual, no need to select layers for update - just don't input the path if you dont wanna
            update_checkbutton.grid(row=0, column=0, sticky="W", padx=(10,0), pady=10)
        if export_checkbutton: export_checkbutton.grid(row=0, column=1, sticky="W", padx=(10,0), pady=10)
        if update_entry_frame: update_entry_frame.grid(row=0, column=2, sticky="EW")

    # Secondary draw of layer list item, to avoid doing unnecessary work. Does less formatting stuff, etc.
    def redraw_layer_list_item(self, layer_index):
        layer = self.json_data["layer_data"][layer_index]
        frame = self.layer_frame_list[layer_index]
        bg_color = gui_shared.secondary_bg if layer_index % 2 else gui_shared.bg_color

        # Destroy existing buttons and such
        for widget in frame.winfo_children():
            widget.destroy()

        update_checkbutton = None
        export_checkbutton = None
        update_entry_frame = None

        # Update checkbutton will only appear if the user is updating the layers, and if it's a normal (i.e. non-cosmetic/border) layer
        if self.updating.get():
            update_checkbutton = tk.Checkbutton(frame, text=f"Update", command=self.check_update_set_all,
                bg=bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, variable=self.layer_update_list[layer_index])
            if layer.get("is_cosmetic_only"):
                update_checkbutton.config(state="disabled")
            ToolTip(update_checkbutton, "If checked, the program will update this layer's unique pose images according to the option selected on the right.")

            # Label, entry, and button for selecting filepath. Will only appear if the user is updating pose images w/ manually selected layers.
            if self.update_type.get() == UPDATE_INDIVIDUAL_MANUAL:
                update_entry_frame = tk.Frame(frame, bg=bg_color)

                tk.Label(update_entry_frame, bg=bg_color, fg=gui_shared.fg_color, text="Update Image:").pack(side="left", padx=(10,5), pady=10)

                entry = add_widget(tk.Entry, update_entry_frame, {"textvariable": self.layer_path_list[layer_index], "width": 1}, {"text": "Enter the path to the image you want to use to update this layer's pose images."})
                entry.pack(side="left", fill="x", expand=True, pady=10)

                button = tk.Button(update_entry_frame, bg=gui_shared.button_bg, fg=gui_shared.fg_color, text="📁",
                    command=lambda s=self.layer_path_list[layer_index], f=[("Image file", "*.png")]: gui_shared.ask_open_file_for_stringvar(s,f))
                button.pack(side="left", padx=10, pady=10)
                ToolTip(button, "Select the image you want to use to update this layer's pose images.")

        # Export checkbutton if the user is exporting the layers
        if self.exporting.get():
            export_checkbutton = tk.Checkbutton(frame, text=f"Export", command=self.check_export_set_all,
                bg=bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, variable=self.layer_export_list[layer_index])

            ToolTip(export_checkbutton, "If checked, the program will include this layer in the export according to the option selected on the right.")

        if update_checkbutton and self.update_type.get() != UPDATE_INDIVIDUAL_MANUAL: # If manual, no need to select layers for update - just don't input the path if you dont wanna
            update_checkbutton.grid(row=0, column=0, sticky="W", padx=(10,0), pady=10)
        if export_checkbutton: export_checkbutton.grid(row=0, column=1, sticky="W", padx=(10,0), pady=10)
        if update_entry_frame: update_entry_frame.grid(row=0, column=2, sticky="EW")

    # Simple for loop so that tkinter button commands will be simpler
    def redraw_layer_list_items(self):
        # self.layer_list_frame.pack_propagate(True)
        # self.layer_list_frame.update_idletasks()

        if self.json_data != None:
            self.redraw_layer_list_header()
            for i in range(len(self.json_data["layer_data"])):
                self.redraw_layer_list_item(i)
        
        self.resize_layer_list()

    # Check if the update all checkbutton should be checked or unchecked
    def check_update_set_all(self):
        for var in self.layer_update_list:
            if var != None and var.get() == False:
                self.layer_update_all.set(False)
                return
        self.layer_update_all.set(True)

    # Check if the export all checkbutton should be checked or unchecked
    def check_export_set_all(self):
        for var in self.layer_export_list:
            if var != None and var.get() == False:
                self.layer_export_all.set(False)
                return
        self.layer_export_all.set(True)

    def resize_layer_list(self): # TODO rename maybe, an inline func in setup_ui shares the name without the "self." before
        self.layer_list_frame.pack_propagate(True)
        self.layer_list_frame.update_idletasks()
        self.layer_list_frame.configure(width=self.layer_canvas_frame.winfo_width(), height=self.layer_list_frame.winfo_reqheight())
        self.layer_list_frame.pack_propagate(False)

    # For scrolling layer list
    def on_left_frame_mousewheel(self, event):
        delta = -1 * (event.delta // 120)
        self.layer_canvas.yview_scroll(delta, "units")

    # Load the json specified at the given or selected path
    def load_json(self, path = None):
        # If a path was not passed as parameter, ask for one
        if not path: path = filedialog.askopenfilename(title="Select a sheet data .json, in the same folder as its pose images", defaultextension=".json", filetypes=[("Json File", "*.json")]) # TODO: make sure file dialogs are consistent with filetypes, titles, etc.
        if path: # If a path was not passed as param nor given through filedialog, don't continue
            with open(path) as json_file:
                self.json_data = json.load(json_file) #could unindent after this? i.e. self.json_data's been set, so we don't need to keep the actual json file open

            self.input_folder_path = os.path.dirname(path)
            self.loaded_json_filename_label.config(text=f"Filename: {os.path.basename(path)}")
            self.loaded_json_sheetname_label.config(text=f"Sheet name: {self.json_data['header']['name']}")

            # It's *technically* possible to have a menu_exportsheet without a loaded json, and the generate buttons and stuff were disabled when that was the case.
            # Now, it's not possible through normal means, so no need to have this check.
            #
            # THAT SAID, the export button is still disabled upon load. i dont wanna get rid of that, so this is fine
            self.generate_ended() # does all necessary stuff at once

            # If something's been generated already, reset the progress indicators
            self.update_progress(0, "", "")

            # Empty output folder path. (In theory, might not be something people want if they're trying to export a lotta things into one place. But this seems safer, and will probably prevent more confusion than it creates)
            self.output_folder_path.set("")

            # Set image size
            self.image_size = (self.json_data["header"]["width"], self.json_data["header"]["height"])

            # Draw layer list
            self.draw_layer_list()
            
            # Reset the progress bar
            self.check_reset_progress()

    # Generate button (export button, actually) has been pressed, so communicate that to main process and provide generation info
    def generate_button_pressed(self):

        if self.exporting.get() and not self.output_folder_path.get():
            messagebox.showwarning("Wait!", "You must select an output folder first")
            return

        if self.updating.get():
            self.communicate_update_to_main()
        if self.exporting.get():
            self.communicate_export_to_main()

    # Ask the main process to start an update task
    def communicate_update_to_main(self):
        # TODO checks for filepaths: if multilayer doesnt exist then return, etc

        try:
            update_type = self.update_type.get()

            selected_layers = [] # Array of ints

            if self.update_type == UPDATE_INDIVIDUAL_MANUAL:
                for i, var in enumerate(self.layer_path_list):
                    if var != None:
                        path = var.get()
                        if path != None:
                            selected_layers.append(i)
            else:    
                for i, var in enumerate(self.layer_update_list): # Append selected layer to list
                    if var != None:
                        if var.get():
                            selected_layers.append(i)
            
            # Data that will be saved to a temporary file for easy transfer to main process
            temp_json_data = {
                "data": self.json_data,
                "input_folder_path": self.input_folder_path,
                "selected_layers": selected_layers
            }

            match update_type:
                case 0: # UPDATE_INDIVIDUAL_AUTO
                    num_layers = len(self.json_data["layer_data"])
                    number_of_characters = len(str(num_layers))

                    paths = []

                    for i in range(num_layers): # Try to find a file with a path matching the default export name for individual layer images
                        path = (
                            os.path.join(self.input_folder_path,
                            f"{self.json_data["header"]["name"]}_layer{str(i + 1).rjust(number_of_characters, '0')}_{self.json_data["layer_data"][i]["name"]}_export.png"))
                        if os.path.exists(path) and (i in selected_layers): # No need to pass selected_layers here - we can simply not send the not-selected paths if they're found
                            paths.append(path)
                        else:
                            paths.append(None)

                    temp_json_data.update({"image_paths": paths})

                case 1: # UPDATE_INDIVIDUAL_MANUAL
                    paths = []
                    for var in self.layer_path_list:
                        path = var.get()
                        if not path: path = None
                        paths.append(path)

                    temp_json_data.update({"image_paths": paths})

                case 2: # UPDATE_MULTILAYER_FILE
                    temp_json_data.update({"multilayer_file_path": self.update_multilayer_file_path.get()})

            # Save data to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_json_file:
                json.dump(temp_json_data, temp_json_file)

                # Subtypes. 0 and 1 are shared, as there is no difference in what generate_main.py or generate.py have to do - that's all handled here
                temp = ["update_pose_images_with_images", "update_pose_images_with_images", "update_pose_images_with_multilayer_file"]

                # Output data to main process
                gui_shared.communicate_to_main("generate", temp_json_file.name.replace('\\', '/'), temp[update_type])
        
        except Exception as e:
            gui_shared.communicate_to_main("error", e)

    def communicate_export_to_main(self):
        try:
            # Data that will be saved to a temporary file for easy transfer to main process
            temp_json_data = {
                "data": self.json_data,
                "input_folder_path": self.input_folder_path,
                "output_folder_path": self.output_folder_path.get(),
                "file_type": self.file_type_option.get().split(" ")[0] # The multilayer files have a second part to show the program(s) the files are for. This splits that off.
            }

            if self.export_type.get() != 3: # i.e. if anything other than update pose images:
                selected_layers = [] # Array of ints

                for i, var in enumerate(self.layer_export_list): # Append selected layer to list
                    if var != None:
                        if var.get():
                            selected_layers.append(i)
                
                # Update export-type-specific data to temp_json_data             
                temp_json_data.update({"selected_layers": selected_layers, "pose_type": self.pose_type.get()})

            # Save data to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_json_file:
                json.dump(temp_json_data, temp_json_file)

                # Generation types, formatted to work with radio buttons
                subtypes = ["export_sheet_image", "export_layer_images", "export_multilayer_file"]

                # Output data to main process
                gui_shared.communicate_to_main("generate", temp_json_file.name.replace('\\', '/'), subtypes[self.export_type.get()])
        except Exception as e:
            gui_shared.communicate_to_main("error", e)

    # Update menu progressbar (COULD add this stuff to the class that menus will inherit from)
    def update_progress(self, value, header_text, info_text):
        self.progress_bar["value"] = value
        self.progress_header_label.configure(text=header_text)
        self.progress_info_label.configure(text=info_text)
    
    # Send output to main process, requesting that the process be cancelled
    def cancel_generate(self):
        print(json.dumps({"type": "cancel"}), flush=True)
    
    # Disable export/quit buttons, enable cancel button
    def generate_begun(self):
        self.export_button.configure(state="disabled")
        self.load_button.configure(state="disabled")
        self.back_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")

    # Enable export/quit buttons, disable cancel button
    def generate_ended(self):
        self.export_button.configure(state="normal")
        self.load_button.configure(state="normal")
        self.back_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")
    
    # After an export, sometimes another export is in order. However, because the progress bar remains filled, I often get confused about
    # what I'm supposed to be doing.
    def check_reset_progress(self):
        if self.back_button.cget('state') == 'normal':
            self.update_progress(0, "", "")