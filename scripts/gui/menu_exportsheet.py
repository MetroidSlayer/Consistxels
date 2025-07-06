import json
import os
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image

import scripts.gui.gui_shared as gui_shared
from scripts.gui.gui_shared import add_widget
from scripts.classes.tooltip import ToolTip

# Menu for exporting sprite sheets, layers, and pose images for already-generated sheet data
class Menu_ExportSheet(tk.Frame):
    def __init__(self, master, change_menu_callback, load_path = None): # TODO change load to only accept sheetdata_generated json type
        super().__init__(master) # Initialize menu's tkinter widget
        self.input_folder_path = None # Input folder path must be stored so images can be loaded later
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

        # Will contain the widgets in which 
        self.layer_list = []

        # For resizing the layer widgets so they fit in the canvas.
        # (Work on this a little more - it works, but this one's a bit clunky I think)
        def resize_layer_list(_ = None):
            self.layer_canvas_frame.update_idletasks()
            self.scrollable_frame.configure(width = self.layer_canvas_frame.winfo_width())
            for widget in self.scrollable_frame.winfo_children():
                widget.configure(width=self.layer_canvas_frame.winfo_width())

        self.left_frame.bind("<Configure>", resize_layer_list)

        self.layer_canvas.pack(side="left", fill="both", expand=True)

        # Bind mousewheel for scrolling left frame
        gui_shared.bind_event_to_all_children(self.left_frame,"<MouseWheel>",self.on_left_frame_mousewheel)

        # Export options

        export_options_frame = tk.Frame(self.right_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        export_options_frame.pack(fill="both", expand=True)

        tk.Label(export_options_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Export type:").pack(anchor="w", padx=10, pady=10)

        # Stores radio button value
        # 0: single image, 1: individual layer image(s), 2: multi-layer file, 3: update pose images
        self.export_type = tk.IntVar()
        self.export_type.set(0)

        self.last_export_type = 0 # To check if anything in the menu needs to be changed

        # Upon radio button selection, check if the menu needs to be changed
        def check_update_layer_list():
            curr_export_type = self.export_type.get()
            
            # Should be made more modular, and expanded to enable/disable relevant fields/buttons
            if (curr_export_type < 3) != (self.last_export_type < 3):
                if curr_export_type == 3: # TODO TODO TODO probably replace with a variable, in case i wanna mess with the indexes later at any point
                    self.draw_layer_entries()
                    self.output_folder_entry.config(state="disabled")
                    self.output_folder_button.config(state="disabled")
                    self.output_use_current_folder_button.config(state="disabled")
                else:
                    self.draw_layer_checkbuttons()
                    self.output_folder_entry.config(state="normal")
                    self.output_folder_button.config(state="normal")
                    self.output_use_current_folder_button.config(state="normal")
            
            if curr_export_type in [0,3]:
                self.unique_pose_images_only_checkbutton.config(state="disabled")
            else:
                self.unique_pose_images_only_checkbutton.config(state="normal")

            self.last_export_type = curr_export_type

            self.check_reset_progress()

        # Export type radio buttons

        radio_single = tk.Radiobutton(export_options_frame, text="Single merged image", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, variable=self.export_type, value=0, command=check_update_layer_list)
        radio_single.pack(anchor="w", padx=10)
        ToolTip(radio_single, "Export one image containing all selected layers merged together.")

        radio_layers = tk.Radiobutton(export_options_frame, text="Individual layer image(s)", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, variable=self.export_type, value=1, command=check_update_layer_list)
        radio_layers.pack(anchor="w", padx=10)
        ToolTip(radio_layers, "Export an image for each selected layer.")

        radio_update = tk.Radiobutton(export_options_frame, text="Update pose images", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, variable=self.export_type, value=3, command=check_update_layer_list)
        radio_update.pack(anchor="w", padx=10, pady=10)
        ToolTip(radio_update, """Input new versions of layer images. Existing pose images in this folder will be updated. As long as the first unique instance of a pose image has been changed, that change will be reflected in the pose images. You can then export an entire sheet with the updated pose images.\n\n(This is what the "Unique Pose Image" and "Source Image" options are generally made for, but you don't necessarily *need* to use an image that was generated with either option.)""")

        # Controls whether only unique images are exported. Does not work for single image or update pose images
        self.unique_pose_images_only = tk.BooleanVar()
        self.unique_pose_images_only_checkbutton = tk.Checkbutton(export_options_frame, text="Only show unique pose images", bg=gui_shared.bg_color, fg=gui_shared.fg_color,
            selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, variable=self.unique_pose_images_only, state="disabled", command=self.check_reset_progress)
        self.unique_pose_images_only_checkbutton.pack(anchor="w", padx=10, pady=10)
        ToolTip(self.unique_pose_images_only_checkbutton,"""Exported layers will only contain unique pose images. They'll be positioned where they were initially found during the "Generate Sprite Sheet Data" search, so they might be a little spread out.\n\nIn general, if you're transferring a number of poses from one sheet to another, this will be much faster than opening each pose image individually. After modifying unique-only layers, use the "Update pose images" export type to make sure individual pose images are up-to-date, then generate the whole sheet.\n\n(Does not work with the "Single merged image" or "Update pose images" export types.)""")

        # Eventually, file type option menu should go here.
        # The options should be different depending on if external_filetype is chosen;
        # usually, it should be normal stuff, .png and the like, but w/ external_filetype
        # it should be .psd, .aseprite, etc.

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

    # Draw checkbuttons in a list format for choosing which layers to export
    def draw_layer_checkbuttons(self):
        # Destroy current layer list
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Specific checkbuttons for selecting/deselecting all layers at once
        all_checkbutton_frame = tk.Frame(self.scrollable_frame, bg=gui_shared.button_bg, width=0)
        all_checkbutton_frame.pack(side="top", fill="x", expand=True)

        # Doesn't need to be stored anywhere, since it doesn't directly determine anything - it's just for better usability
        all_checkbutton_var = tk.BooleanVar()

        # Set each layer to whatever all_checkbutton_var is set to
        def set_all():
            for var in self.layer_list:
                var.set(all_checkbutton_var.get())

            self.check_reset_progress()

        # ALL checkbutton selectcolors are now field_bg, as it probably looks better. but CONSIDER changing it back to button_bg
        all_checkbutton = tk.Checkbutton(all_checkbutton_frame, text=f"ALL", bg=gui_shared.button_bg, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, variable=all_checkbutton_var, command=set_all)
        all_checkbutton.pack(side="left", padx=10, pady=10)
        ToolTip(all_checkbutton, "Check to select or deselect all layers at once.")
        
        # Reset layer list
        # (Layers list contains tk.___Var()s, not widgets)
        self.layer_list = []

        # Create a checkbutton for each layer
        for i, layer in enumerate(self.json_data["layer_data"]):
            checkbutton_var = tk.BooleanVar()
            
            # BG color changes depending on if odd or even, to make list a little more readable at a glance
            checkbutton_frame = tk.Frame(self.scrollable_frame, bg=gui_shared.secondary_bg if i % 2 else gui_shared.bg_color)
            checkbutton_frame.pack(side="top", fill="x", expand=True)
            
            # Update the ALL checkbutton if something's deselected
            # (Just to make it more satisfying, maybe make it also update the ALL checkbutton if layers are enabled manually? idk not necessary)
            def update_deselect(var=checkbutton_var):
                if not var.get(): all_checkbutton_var.set(False)

                self.check_reset_progress()
            
            checkbutton = tk.Checkbutton(checkbutton_frame, text=f"{i+1}: {layer["name"]}", bg=gui_shared.secondary_bg if i % 2 else gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, variable=checkbutton_var, command=update_deselect)
            checkbutton.pack(side="left", padx=10, pady=10)
            ToolTip(checkbutton, f'Check to include layer {i+1} ("{layer["name"]}") in exports.')

            self.layer_list.append(checkbutton_var)

            # Configure height and width manually
            checkbutton_frame.update_idletasks()
            checkbutton_frame.configure(width=self.scrollable_frame.cget('width'), height=checkbutton_frame.winfo_height())
            checkbutton_frame.pack_propagate(False)

        # Set ALL to True initially, since I think most people would prefer to export all layers at once anyway
        all_checkbutton.select()
        set_all()

        # Bind mousewheel
        gui_shared.bind_event_to_all_children(self.scrollable_frame, "<MouseWheel>", self.on_left_frame_mousewheel)

    # Draw labels, entries, and buttons in a list format
    def draw_layer_entries(self):
        # Destroy current layer list
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Reset layer list
        self.layer_list = []

        # Bandaid fix for the inconvenient process of inputting the files into the entries
        all_frame = tk.Frame(self.scrollable_frame, bg=gui_shared.button_bg)
        all_frame.pack(side="top", fill="x", expand=True)

        all_frame.grid_columnconfigure(0, weight=1)
        all_frame.grid_columnconfigure(1, weight=5)

        tk.Label(
                all_frame, text="ALL", bg=gui_shared.button_bg, fg=gui_shared.fg_color
            ).pack(side="left", padx=(10,5), pady=10)
        
        def autofill():
            num_layers = len(self.json_data["layer_data"])
            number_of_characters = len(str(num_layers))

            for i in range(num_layers):
                path = (
                    os.path.join(self.input_folder_path,
                    f"{self.json_data["header"]["name"]}_layer{str(i + 1).rjust(number_of_characters, '0')}_{self.json_data["layer_data"][i]["name"]}_export.png"))
                if os.path.exists(path):
                    self.layer_list[i].set(path)
        
        all_autofill_button = tk.Button(all_frame, text="Autofill", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=autofill)
        all_autofill_button.pack(side="left", padx=10, pady=10)
        ToolTip(all_autofill_button, "Attempt to find image files with names that match the default individual layer export filenames. If a matching file is found, the respective text entry box is filled with the image path. If they don't, the entry is left blank.")

        # Create widgets for each layer
        for i, layer in enumerate(self.json_data["layer_data"]):
            frame = tk.Frame(self.scrollable_frame, bg=gui_shared.bg_color if i % 2 else gui_shared.secondary_bg)
            frame.pack(side="top", fill="x", expand=True)

            frame.grid_columnconfigure(0, weight=1)
            frame.grid_columnconfigure(1, weight=5)

            entry_var = tk.StringVar()

            tk.Label(
                frame, text=f"{i+1}: {layer["name"]}", bg=gui_shared.bg_color if i % 2 else gui_shared.secondary_bg, fg=gui_shared.fg_color
            ).pack(side="left", padx=(10,5), pady=10)

            entry = add_widget( # TODO: make widths of entry widgets consistent. At the moment it looks a little bad
                tk.Entry, frame, {'textvariable':entry_var, 'width':1}, {'text':"Enter the path to the image that will update all pose images sourced from this layer."}
            )
            entry.pack(side="left", fill="x", expand=True, pady=10)

            # Open filedialog, get new image, check size
            def select_new_image(var=entry_var):
                # Get path from filedialog
                path = filedialog.askopenfilename(title="Select a new image", filetypes=[("Image File", "*.png;*.jpg;*.jpeg")])

                if path and gui_shared.warn_image_valid(path):
                    
                    with Image.open(path) as image:
                        if self.image_size != image.size:
                            messagebox.showwarning("Warning!", f"All images must be the same size.\nThe original sprite sheet is {self.image_size[0]}x{self.image_size[1]}, but the selected image is {image.size[0]}x{image.size[1]}.")
                            return
                    
                    var.set(path) # Set tk.StringVar() to path
                    self.check_reset_progress()

            output_folder_button = tk.Button(frame, text="📁", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=select_new_image)
            output_folder_button.pack(side="left", padx=10, pady=10)
            ToolTip(output_folder_button, "Open a file dialog and select the image that will update all pose images sourced from this layer.")

            self.layer_list.append(entry_var)

            # Configure height and width manually
            frame.update_idletasks()
            frame.configure(width=self.scrollable_frame.cget('width'), height=frame.winfo_height())
            frame.pack_propagate(False)

        # Bind mousewheel
        gui_shared.bind_event_to_all_children(self.scrollable_frame, "<MouseWheel>", self.on_left_frame_mousewheel)

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

                # Check radiobutton var. Depending on what's selected, create either checkbuttons or entries
                if self.export_type.get() == 3:
                    self.draw_layer_entries()
                else:
                    self.draw_layer_checkbuttons()
            
            self.check_reset_progress()

    # Generate button (export button, actually) has been pressed, so communicate that to main process and provide generation info
    def generate_button_pressed(self):

        output_folder_path = self.output_folder_path.get()

        # folder path needs to be treated differently depending on the export type chosen

        if output_folder_path or self.export_type.get() == 3:
            try:
                # Data that will be saved to a temporary file for easy transfer to main process
                temp_json_data = {"data": self.json_data, "input_folder_path": self.input_folder_path, "output_folder_path": output_folder_path} # technically dont need input in generate_sheet, or output in update

                if self.export_type.get() != 3: # i.e. if anything other than update pose images:
                    selected_layers = [] # Array of ints

                    for i, checkbutton in enumerate(self.layer_list): # Append selected layer to list
                        if checkbutton.get(): selected_layers.append(i)
                    
                    # Update export-type-specific data to temp_json_data
                    temp_json_data.update({"selected_layers": selected_layers, "unique_only": self.unique_pose_images_only.get()})                
                else:
                    new_image_paths = [] # Array of strings/paths

                    for entry_var in self.layer_list: # Append path to list
                        new_image_path = entry_var.get()
                        if new_image_path == "": new_image_path = None # Still not sure what's given if an entry is empty. Ought to test sometime

                        if new_image_path and not gui_shared.check_image_valid(new_image_path)[0]:
                            messagebox.showwarning("Warning!", "At least one image is invalid. Check that they exist and are the correct filetype.")
                            return

                        new_image_paths.append(new_image_path)

                    # Update export-type-specific data to temp_json_data
                    temp_json_data.update({"new_image_paths": new_image_paths})

                # Save data to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_json_file:
                    json.dump(temp_json_data, temp_json_file)

                    # Generation types, formatted to work with radio buttons
                    types = ["generate_sheet_image", "generate_layer_images", "generate_external_filetype", "generate_updated_pose_images"]
                    # Output data to main process
                    print(json.dumps({"type": types[self.export_type.get()], "val": temp_json_file.name.replace('\\', '/')}), flush=True)
            except Exception as e:
                print(json.dumps({"type": "error", "val": e}), flush=True)
        else: # If not all necessary info's been filled out, or if something else is wrong (make this more extensive if necessary)
            warning_output = ""

            if not output_folder_path:
                if warning_output != "": warning_output += "\n"
                warning_output += "You must select an output folder first"

            messagebox.showwarning("Wait!", warning_output)
    
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