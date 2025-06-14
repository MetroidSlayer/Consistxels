import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tooltip import ToolTip
from PIL import Image, ImageColor
import json
# from generate import adjust_offset_coordinates
import gui_shared
from gui_shared import add_widget

import tempfile

class Menu_LoadJson(tk.Frame):
    def __init__(self, master, change_menu_callback, load_path = None):
        super().__init__(master)
        
        # gui_shared.bg_color = "#2e2e2e"
        # gui_shared.fg_color = "#ffffff"
        # gui_shared.secondary_bg = "#3a3a3a"
        # gui_shared.secondary_fg = "#6a6a6a"
        # gui_shared.button_bg = "#444"
        # gui_shared.field_bg = "#222222"

        # self.separator_style = ttk.Style().configure("Custom.TSeparator", background=gui_shared.secondary_fg)

        # self.color_transparent = ImageColor.getrgb("#00000000")

        self.input_folder_path = None

        self.configure(bg=gui_shared.bg_color)

        # self.setup_ui(change_menu_callback, load_path)
        self.after(0, self.setup_ui, change_menu_callback, load_path)
    
    def setup_ui(self, change_menu_callback, load_path = None):

        # Header
        self.header = tk.Frame(self, bg=gui_shared.bg_color)
        self.header.pack(fill="x", padx=2)
        # self.header = add_widget(tk.Frame, self, placement_func="pack", placement_args={"fill":"x", "padx":2})

        # Header left:
        
        # Load button
        self.load_button = tk.Button(self.header, text="📁 Load", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=self.load_json)
        self.load_button.pack(padx=(12,10), pady=10, side="left")
        ToolTip(self.load_button, "Load a .json file containing pose data. Must be located in the same folder as its pose images.")

        # Header right:

        # Back button

        self.back_button = tk.Button(self.header, text="Back to Main Menu", bg=gui_shared.button_bg, fg=gui_shared.danger_fg, command=lambda: change_menu_callback("Main"))
        self.back_button.pack(side="right", padx=10, pady=10)
        ToolTip(self.back_button, "...Come on, this one is self explanatory.", False, True, 2000)

        
        # Main frame
        self.main_frame = tk.Frame(self, bg=gui_shared.bg_color)
        self.main_frame.pack(fill="both", expand=True)

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

        paned_window.add(self.left_frame, minsize=400, stretch="always")
        paned_window.add(self.right_frame, minsize=400, stretch="always")

        # Layer list header
        layer_header = tk.Frame(self.left_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        layer_header.pack(side="top", fill="x")

        # json_label_frame = tk.Frame(layer_header, bg=gui_shared.bg_color)
        # json_label_frame.pack(side="top", padx=10, pady=10)

        # self.loaded_json_label = tk.Label(json_label_frame, text="No .json loaded", bg=gui_shared.bg_color, fg=gui_shared.fg_color)
        self.loaded_json_label = tk.Label(layer_header, text="No .json loaded", bg=gui_shared.bg_color, fg=gui_shared.fg_color)
        # self.loaded_json_label.pack(side="left")
        self.loaded_json_label.pack(side="top", padx=10, pady=10, anchor="w")

        # layer_label_frame = tk.Frame(layer_header, bg=gui_shared.bg_color)
        # layer_label_frame.pack(side="top", padx=10, pady=(0,10))

        # layer_label = tk.Label(layer_label_frame, text="Layers:", bg=gui_shared.bg_color, fg=gui_shared.fg_color)
        layer_label = tk.Label(layer_header, text="Layers:", bg=gui_shared.bg_color, fg=gui_shared.fg_color)
        # layer_label.pack(side="left")
        layer_label.pack(side="top", padx=10, pady=(0,10), anchor="w")

        # Layer list
        layer_list_container_frame = tk.Frame(self.left_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        layer_list_container_frame.pack(side="top", fill="both", expand=True)

        layer_canvas_frame = tk.Frame(layer_list_container_frame, bg=gui_shared.bg_color, width=0)
        layer_canvas_frame.pack(side="left", fill="both", expand=True)
        
        self.layer_canvas = tk.Canvas(layer_canvas_frame, bg=gui_shared.bg_color, highlightthickness=0, width=0)

        self.layer_scrollbar = tk.Scrollbar(layer_list_container_frame, orient="vertical", command=self.layer_canvas.yview)
        self.layer_scrollbar.pack(side="left", fill="y", padx=(2,0), pady=0)

        self.scrollable_frame = tk.Frame(self.layer_canvas, bg=gui_shared.bg_color)

        # Bind scrolling
        self.scrollable_frame.bind("<Configure>", lambda e: self.layer_canvas.configure(scrollregion=self.layer_canvas.bbox("all")))

        # Create canvas in which to show layer info
        self.layer_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.layer_canvas.configure(yscrollcommand=self.layer_scrollbar.set)

        self.layer_list = []

        def resize_layer_list(_ = None):
            self.left_frame.update()
            self.scrollable_frame.configure(width = layer_canvas_frame.winfo_width())

            for widget in self.scrollable_frame.winfo_children():
                # widget.configure(width=layer_canvas_frame.winfo_width(), height=widget.winfo_height())
                widget.configure(width=layer_canvas_frame.winfo_width())
                # widget.pack_propagate(False)
            
            # for layer in self.layer_list:
            #     layer["frame"].configure(width=layer_canvas_frame.winfo_width())

        self.left_frame.bind("<Configure>", resize_layer_list)

        self.layer_canvas.pack(side="left", fill="both", expand=True)

        gui_shared.bind_event_to_all_children(self.left_frame,"<MouseWheel>",self.on_left_frame_mousewheel)


        # Export options

        export_options_frame = tk.Frame(self.right_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        export_options_frame.pack(fill="both", expand=True)

        tk.Label(export_options_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Export type:").pack(anchor="w", padx=10, pady=10)

        self.export_type = tk.IntVar()
        self.export_type.set(0)

        self.last_export_type = 0

        def check_update_layer_list():
            curr_export_type = self.export_type.get()
            
            if (curr_export_type < 3) != (self.last_export_type < 3):
                if curr_export_type == 3:
                    self.draw_layer_entries()
                else:
                    # print("gothere")
                    self.draw_layer_checkbuttons()
            
            # print(self.last_export_type, curr_export_type)

            self.last_export_type = curr_export_type

        radio_single = tk.Radiobutton(export_options_frame, text="Single merged image", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, variable=self.export_type, value=0, command=check_update_layer_list)
        radio_single.pack(anchor="w", padx=10)
        ToolTip(radio_single, "Export one image containing all selected layers merged together.")

        radio_multiple = tk.Radiobutton(export_options_frame, text="Multiple individual layer images", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, variable=self.export_type, value=1, command=check_update_layer_list)
        radio_multiple.pack(anchor="w", padx=10)
        ToolTip(radio_multiple, "Export an image for each selected layer.")

#         radio_external_filetype = tk.Radiobutton(export_options_frame, text="Multi-layered file (for external editor)", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, variable=self.export_type, value=2, command=check_update_layer_list)
#         radio_external_filetype.pack(anchor="w", padx=10)
#         ToolTip(radio_external_filetype, """
# (NOT IMPLEMENTED YET!!!) Export a file containing the selected layers that can be opened in an external editor of your
# choice.

# Supported filetypes: .aseprite, .psd
#         """.strip())

        radio_update = tk.Radiobutton(export_options_frame, text="Update pose images", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, variable=self.export_type, value=3, command=check_update_layer_list)
        radio_update.pack(anchor="w", padx=10, pady=10)
        ToolTip(radio_update, """
Input new versions of layer images. Existing pose images in this folder will be updated. As long as
the first unique instance of a pose image has been changed, that change will be reflected in the
pose images. You can then export an entire sheet with the updated pose images.

(This is what the "Unique Pose Image" and "Source Image" options are generally made for, but you
don't necessarily *need* to use an image that was generated with either option.)
        """.strip())

        # make not work for full-sheet export? probably??? just to avoid confusion?
        # ALSO disable for update_unique_images. so this is really only for multiple layers or for multilayer filetype
        self.unique_pose_images_only = tk.BooleanVar()
        unique_pose_images_only_checkbutton = tk.Checkbutton(export_options_frame, text="Only show unique pose images", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, variable=self.unique_pose_images_only)
        unique_pose_images_only_checkbutton.pack(anchor="w", padx=10, pady=10)
        ToolTip(unique_pose_images_only_checkbutton, """
Exported layers will only contain unique pose images. They'll be positioned where they were
initially found during the "Generate Pose Data" search, so they might be a little spread out.

In general, if you're transferring a number of poses from one sheet to another, this will be much
faster than opening each pose image individually. After modifying unique-only layers, use the
"Update pose images" export type to make sure individual pose images are up-to-date, then generate
the whole sheet.

(NOT RECOMMENDED with the "Single merged image" export type.)
""".strip())

        # file type optionmenu

        output_path_frame = tk.Frame(self.right_frame, bg=gui_shared.bg_color, highlightthickness=1, highlightbackground=gui_shared.secondary_fg)
        output_path_frame.pack(fill="both", expand=True, anchor="s")

        tk.Label(output_path_frame, text="Output folder path:", bg=gui_shared.bg_color, fg=gui_shared.fg_color).pack(side="left", padx=(10,5), pady=10)

        # TODO TODO TODO disabled output folder path if "update" is selected.
        self.output_folder_path = tk.StringVar()
        add_widget(
            tk.Entry, output_path_frame, {'textvariable':self.output_folder_path}, {'text':"""
Enter the path to the folder where the exported images will be output.

(It's recommended that you choose a new, EMPTY folder! Choosing an existing one will clutter up
your files at best, and overwrite existing data at worst. That said, if you WANT to overwrite
existing data, go for it.)
        """.strip()}
        ).pack(side="left", fill="x", expand=True, pady=10)

        def select_output_folder_path():
            self.output_folder_path.set(filedialog.askdirectory(title="Select an output folder (preferably empty)"))

        output_folder_button = tk.Button(output_path_frame, text="📁", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=select_output_folder_path)
        output_folder_button.pack(side="left", padx=10, pady=10)
        ToolTip(output_folder_button, """
Open a file dialog and select the folder where the exported images will be output.

(It's recommended that you choose a new, EMPTY folder! Choosing an existing one will clutter up
your files at best, and overwrite existing data at worst. That said, if you WANT to overwrite
existing data, go for it.)
        """.strip())


        
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
        # self.progress_label.grid(padx=10, pady=10, row=1, column=1, columnspan=2)

        # self.top_frame = tk.Frame(self, bg=gui_shared.bg_color)
        # self.top_frame.pack(fill="x", padx=10, pady=5)

        # load_json_button = tk.Button(self.top_frame, text="Load JSON", command=self.load_json, bg=gui_shared.button_bg, fg=gui_shared.fg_color)
        # load_json_button.pack(side="left", padx=5)
        # ToolTip(load_json_button, "Load a valid JSON file.")

        # self.loaded_json_label = tk.Label(self.top_frame, text="No .json loaded", bg=gui_shared.bg_color, fg=gui_shared.fg_color)
        # self.loaded_json_label.pack(side="left", padx=5)

        # # ttk.Separator(self.top_frame, orient="vertical", style=self.separator_style).pack(fill="y", side="left", padx=5)


        
        # self.mid_frame = tk.Frame(self, bg=gui_shared.bg_color)
        # # self.mid_frame.pack(fill="x", padx=10, pady=5)
        # self.mid_frame.pack(side="left", fill="y", padx=10)


        # # other options
        # # self.include_border = tk.BooleanVar()
        # # include_border_checkbutton = tk.Checkbutton(self.mid_frame, text="Include border in export", bg=gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, variable=self.include_border)
        # # include_border_checkbutton.select()
        # # # include_border_checkbutton.pack(side="left", padx=5)
        # # include_border_checkbutton.grid(row=0, column=0, sticky="w")
        # # ToolTip(include_border_checkbutton, "In exported images, include the border.\n(Recommended for full sprite sheet exports)")
        # # # could instead have an optionmenu where it's, like, "above", "below", "none" in case the position of the border matters

        # # export stuff
        # self.export_sheet_button = tk.Button(self.mid_frame, text="Export Sprite Sheet Image", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=self.export_sprite_sheet, state="disabled")
        # # self.export_sheet_button.pack(padx=5)
        # self.export_sheet_button.grid(row=1, column=0, sticky="w")
        # ToolTip(self.export_sheet_button, "Export the entire sprite sheet as a single image.")

        # # ttk.Separator(self.mid_frame, orient="vertical", style=self.separator_style).pack(fill="y", side="left", padx=5)
 
        
        # self.export_layer_button = tk.Button(self.mid_frame, text="Export Individual Layer Image", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=self.export_layer, state="disabled")
        # # self.export_layer_button.pack(padx=5)
        # self.export_layer_button.grid(row=2, column=0, sticky="w")
        # ToolTip(self.export_layer_button, "Export one layer as an image.")
        
        # self.layer_option = tk.StringVar()
        # self.layer_option.set("")
        # self.export_layer_optionmenu = tk.OptionMenu(self.mid_frame, self.layer_option, "")

        
        # self.export_layer_optionmenu.configure(bg=gui_shared.bg_color, fg=gui_shared.fg_color, activebackground=gui_shared.secondary_bg, activeforeground=gui_shared.fg_color, width=28, anchor="w", justify="left", state="disabled")
        # self.export_layer_optionmenu["menu"].configure(bg=gui_shared.field_bg, fg=gui_shared.fg_color, activebackground=gui_shared.secondary_bg, activeforeground=gui_shared.fg_color)

        # # self.export_layer_optionmenu.pack(side="left", padx=5)
        # self.export_layer_optionmenu.grid(row=2, column=1, sticky="w")
        # ToolTip(self.export_layer_optionmenu, "Choose which layer to export.")





        # # ttk.Separator(self.mid_frame, orient="vertical", style=self.separator_style).pack(fill="y", side="left", padx=5)




        # back_button = tk.Button(self.top_frame, text="Back to Main Menu", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=lambda: change_menu_callback("Main"))
        # back_button.pack(side="right", padx=5)
        # ToolTip(back_button, "...Come on, this one is self explanatory.", False, True, 2000)

        if load_path: self.load_json(load_path)

    def draw_layer_checkbuttons(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        all_checkbutton_frame = tk.Frame(self.scrollable_frame, bg=gui_shared.button_bg, width=0)
        all_checkbutton_frame.pack(side="top", fill="x", expand=True)

        all_checkbutton_var = tk.BooleanVar()

        def set_all():
            for var in self.layer_list:
                var.set(all_checkbutton_var.get())
        # def set_all():
        #     for layer in self.layer_list:
        #         layer["var"].set(all_checkbutton_var.get())

        # ALL checkbutton selectcolors are now field_bg, as it probably looks better. but CONSIDER changing it back to button_bg
        all_checkbutton = tk.Checkbutton(all_checkbutton_frame, text=f"ALL", bg=gui_shared.button_bg, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, variable=all_checkbutton_var, command=set_all)
        all_checkbutton.pack(side="left", padx=10, pady=10)
        ToolTip(all_checkbutton, "Check to select or deselect all layers at once.")

        # all_checkbutton_frame.update()
        # width = self.layer_canvas.winfo_width()
        # height = all_checkbutton_frame.cget('height')
        # all_checkbutton_frame.pack_propagate(False)
        # all_checkbutton_frame.configure(width=width, height=height)
        # all_checkbutton_frame.update()
        
        self.layer_list = []

        for i, layer in enumerate(self.json_data["layer_data"]):
            checkbutton_var = tk.BooleanVar()
            
            checkbutton_frame = tk.Frame(self.scrollable_frame, bg=gui_shared.secondary_bg if i % 2 else gui_shared.bg_color)
            checkbutton_frame.pack(side="top", fill="x", expand=True)
            
            def update_deselect(var=checkbutton_var):
                if not var.get(): all_checkbutton_var.set(False)
            
            checkbutton = tk.Checkbutton(checkbutton_frame, text=f"{i+1}: {layer["name"]}", bg=gui_shared.secondary_bg if i % 2 else gui_shared.bg_color, fg=gui_shared.fg_color, selectcolor=gui_shared.field_bg, onvalue=True, offvalue=False, variable=checkbutton_var, command=update_deselect)
            checkbutton.pack(side="left", padx=10, pady=10)
            ToolTip(checkbutton, f'Check to include layer {i+1} ("{layer["name"]}") in exports.')

            self.layer_list.append(checkbutton_var)
            # self.layer_list.append({"frame":checkbutton_frame, "var":checkbutton_var})

            # checkbutton_frame.pack_propagate(False)
            # checkbutton_frame.configure(width=width, height=height)

            checkbutton_frame.update()
            # checkbutton_frame.configure(width=self.scrollable_frame.winfo_width(), height=checkbutton_frame.winfo_height())
            checkbutton_frame.configure(width=self.scrollable_frame.cget('width'), height=checkbutton_frame.winfo_height())
            checkbutton_frame.pack_propagate(False)

        # all_checkbutton.configure(command=set_all)

        all_checkbutton.select()
        set_all()

        

        gui_shared.bind_event_to_all_children(self.scrollable_frame, "<MouseWheel>", self.on_left_frame_mousewheel)

    def draw_layer_entries(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.layer_list = []

        for i, layer in enumerate(self.json_data["layer_data"]):
            frame = tk.Frame(self.scrollable_frame, bg=gui_shared.bg_color if i % 2 else gui_shared.secondary_bg)
            frame.pack(side="top", fill="x", expand=True)

            entry_var = tk.StringVar()

            tk.Label(frame, text=f"{i+1}: {layer["name"]}", bg=gui_shared.bg_color if i % 2 else gui_shared.secondary_bg, fg=gui_shared.fg_color).pack(side="left", padx=(10,5), pady=10)

            add_widget(
                tk.Entry, frame, {'textvariable':entry_var, 'width':1}, {'text':"Enter the path to the image that will update all pose images sourced from this layer."}
            ).pack(side="left", fill="x", expand=True, pady=10)

            def select_new_image(var=entry_var):
                var.set(filedialog.askopenfilename(title="Select a new image", filetypes=[("Image File", "*.png;*.jpg;*.jpeg")]))
                # TODO SIZE CHECK!!!

            output_folder_button = tk.Button(frame, text="📁", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=select_new_image)
            output_folder_button.pack(side="left", padx=10, pady=10)
            ToolTip(output_folder_button, "Open a file dialog and select the image that will update all pose images sourced from this layer.")

            self.layer_list.append(entry_var)
            # self.layer_list.append({"frame":frame, "var":entry_var})

            frame.update()
            # checkbutton_frame.configure(width=self.scrollable_frame.winfo_width(), height=checkbutton_frame.winfo_height())
            frame.configure(width=self.scrollable_frame.cget('width'), height=frame.winfo_height())
            frame.pack_propagate(False)

        gui_shared.bind_event_to_all_children(self.scrollable_frame, "<MouseWheel>", self.on_left_frame_mousewheel)

    def on_left_frame_mousewheel(self, event):
        delta = -1 * (event.delta // 120)
        self.layer_canvas.yview_scroll(delta, "units")

    def load_json(self, path = None):
        if not path: path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("Json File", "*.json")]) # TODO: GO BACK AND ADD THIS TO OTHER FILE DIALOGS
        if path:
            # json_file = open(path)
            with open(path) as json_file:
                # json_data = json.load(json_file)
                self.json_data = json.load(json_file) #could unindent after this?
                # json_file.close()

                # self.output_folder_path = os.path.dirname(path)
                self.input_folder_path = os.path.dirname(path)
                # self.output_folder_path.set(os.path.dirname(path))
                self.output_folder_path.set(self.input_folder_path)
                self.loaded_json_label.config(text=os.path.basename(path) + " (" + self.json_data["header"]["name"] + ")")

                # self.export_sheet_button.configure(state="normal")
                # self.export_layer_button.configure(state="normal")
                self.generate_ended() # does all necessary stuff at once
                # self.export_layer_button.configure(state="normal")

                # self.export_layer_optionmenu.configure(state="normal")
                # menu = self.export_layer_optionmenu["menu"]
                # menu.delete(0, "end")

                # for layer_name in self.json_data["header"]["layer_names"]:
                # self.image_size = (-1,-1)
                self.image_size = (self.json_data["header"]["width"], self.json_data["header"]["height"])

                # check radiobutton var. depending on what's selected, do either checkbuttons or entries
                if self.export_type.get() == 3:
                    self.draw_layer_entries()
                else:
                    self.draw_layer_checkbuttons()

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
                # if self.json_data["layer_data"]:
                #     # self.layer_option.set(self.json_data["header"]["layer_names"][0])
                #     self.layer_option.set(self.json_data["layer_data"][0]["name"])
                # else:
                #     self.layer_option.set("")
                
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

    def generate_button_pressed(self):
        output_folder_path = self.output_folder_path.get()

        # folder path needs to be treated differently depending on the export type chosen

        # if len(layer_data) > 0 and header["name"] != "" and not duplicate_layer_name and output_folder_path:
        if output_folder_path:
            try:
                temp_json_data = {"data": self.json_data, "input_folder_path": self.input_folder_path, "output_folder_path": output_folder_path} # technically dont need input in generate_sheet, or output in update

                if self.export_type.get() != 3: # i.e. if anything other than update pose images:
                    selected_layers = [] # array of ints
                    for i, checkbutton in enumerate(self.layer_list):
                        if checkbutton.get(): selected_layers.append(i)
                        print("got to if checkbutton.get(): selected_layers.append(i)")
                    # for i, layer in enumerate(self.layer_list):
                    #     if layer["var"].get(): selected_layers.append(i)

                    # temp_json_data = {"selected_layers": selected_layers, "unique_only": self.unique_pose_images_only.get(), "data": self.json_data, "input_folder_path": output_folder_path, "output_folder_path": output_folder_path}
                    temp_json_data.update({"selected_layers": selected_layers, "unique_only": self.unique_pose_images_only.get()})
                else:
                    new_image_paths = []
                    # for i, entry_var in enumerate(self.layer_list):
                    for entry_var in self.layer_list:
                        new_image_path = entry_var.get() # array of strings/paths
                    # for layer in self.layer_list:
                    #     new_image_path = layer["var"].get() # array of strings/paths
                        if new_image_path == "": new_image_path = None
                        new_image_paths.append(new_image_path)

                    # temp_json_data = {"new_image_paths": new_image_paths, "data": self.json_data, "output_folder_path": output_folder_path}
                    temp_json_data.update({"new_image_paths": new_image_paths})

                # print(str(selected_layers))

                with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp_json_file:
                    json.dump(temp_json_data, temp_json_file)


                    types = ["generate_sheet_image", "generate_layer_images", "generate_external_filetype", "generate_updated_pose_images"]
                    # print({"type": types.index(self.export_type.get()), "val": temp_json_file.name.replace('\\', '/')})
                    # print({"type": types[self.export_type.get()], "val": temp_json_file.name.replace('\\', '/')})

                    # print(json.dumps({"type": types.index(self.export_type.get()), "val": temp_json_file.name.replace('\\', '/')}), flush=True)
                    print({"type": types[self.export_type.get()], "val": temp_json_file.name.replace('\\', '/')})
                    print(json.dumps({"type": types[self.export_type.get()], "val": temp_json_file.name.replace('\\', '/')}), flush=True)

            except Exception as e:
                print(json.dumps({"type": "error", "val": e}), flush=True)
        else:
            warning_output = ""

            if not output_folder_path:
                if warning_output != "": warning_output += "\n"
                warning_output += "You must select an output folder first"

            messagebox.showwarning("Wait!", warning_output)
    
    def update_progress(self, value, header_text, info_text):
        self.progress_bar["value"] = value
        self.progress_header_label.configure(text=header_text)
        self.progress_info_label.configure(text=info_text)
    
    def cancel_generate(self):
        print(json.dumps({"type": "cancel"}), flush=True)
    
    def generate_began(self):
        self.export_button.configure(state="disabled")
        self.load_button.configure(state="disabled")
        self.back_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")

    def generate_ended(self):
        self.export_button.configure(state="normal")
        self.load_button.configure(state="normal")
        self.back_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")

    def update_menu(self):
        pass

#     # def load_sprite_sheet(self, json_data, output_folder_path): # add a bunch of checks for these images; do the files actually exist? etc.
#     # def format_sprite_sheet(self, output_folder_path): # add a bunch of checks for these images; do the files actually exist? etc.
#     def format_sprite_sheet(self): # add a bunch of checks for these images; do the files actually exist? etc.
#         header = self.json_data["header"]
#         # output_folder_path = header["output_folder_path"]
#         # layer_info = header["layer_info"]
#         # layer_names = header["layer_names"]
#         layer_data = self.json_data["layer_data"]
#         # pose_objects = self.json_data["pose_objects"]
#         # images = self.json_data["images"]

#         # border_image = Image.open(header["border_image_path"])

#         # with Image.open(self.output_folder_path + "/" + header["border_image_path"]) as border_image:
#         #     sprite_sheet = border_image.copy()
#         #     # border_image.close()

#         # with Image.open(self.output_folder_path + "/" + self.json_data["header"]["border_image_path"]) as border_image:
#         #     size = border_image.size # might be worth saving the size as a property of self?

#         sprite_sheet = Image.new("RGBA", self.image_size, self.color_transparent)

#         # color_transparent = ImageColor.getrgb("#00000000")

#         # for i in range(len(layer_names) - 1, -1, -1): # WHY does it need to go to -1. that feels bad
#         for i in range(len(layer_data) - 1, -1, -1): # WHY does it need to go to -1. that feels bad
            
#             # # curr_layer_name = layer_info[i]["name"]
#             # curr_layer_name = layer_names[i]
#             # # print(curr_layer_name)
#             # layer_image = Image.new("RGBA", sprite_sheet.size, self.color_transparent)

#             # for pose in pose_objects:
#             #     x_position = pose["x_position"]
#             #     y_position = pose["y_position"]

#             #     limb_objects = pose["limb_objects"]
#             #     for limb in limb_objects:
#             #         if limb["name"] == curr_layer_name: # does not work for images wherein different layers have the same name. either support this or prevent entirely
#             #             # images[limb["image_index"]].open()

#             #             x_offset = limb["x_offset"]
#             #             y_offset = limb["y_offset"]

#             #             with Image.open(output_folder_path + "/" + images[limb["image_index"]]) as limb_image:
#             #                 adjusted_image = limb_image.copy()
#             #                 rotate_type = None

#             #                 # MIGHT be some wacky stuff with the offsets!
#             #                 if limb["flip_h"]:
#             #                     adjusted_image = adjusted_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

#             #                 match limb["rotation"]:
#             #                     case 1:
#             #                         # limb_image = limb_image.transpose(Image.Transpose.ROTATE_270)# if not limb["flip_h"] else Image.Transpose.ROTATE_270)
#             #                         rotate_type = Image.Transpose.ROTATE_90 if limb["flip_h"] else Image.Transpose.ROTATE_270
#             #                         # rotate_type = Image.Transpose.ROTATE_270
#             #                         # rotate_type = Image.Transpose.ROTATE_90
#             #                     case 2:
#             #                         # limb_image = limb_image.transpose(Image.Transpose.ROTATE_180)
#             #                         rotate_type = Image.Transpose.ROTATE_180

#             #                         # continue # !!! TODO
#             #                     case 3:
#             #                         # limb_image = limb_image.transpose(Image.Transpose.ROTATE_90)# if not limb["flip_h"] else Image.Transpose.ROTATE_90)
#             #                         rotate_type = Image.Transpose.ROTATE_270 if limb["flip_h"] else Image.Transpose.ROTATE_90
#             #                         # rotate_type = Image.Transpose.ROTATE_90
#             #                         # rotate_type = Image.Transpose.ROTATE_270
#             #                     # case _:
#             #                         # continue # !!! TODO

#             #                 if rotate_type:
#             #                     adjusted_image = adjusted_image.transpose(rotate_type)

#                             # x_offset_adjust, y_offset_adjust = x_offset + x_position, y_position + y_offset
#             #                 # if rotate_type or limb["flip_h"]:
#             #                 #     bound_original_image = limb_image.crop(limb_image.getbbox())
#             #                 #     bound_adjusted_image = adjusted_image.crop(adjusted_image.getbbox())

#             #                 #     # x_offset_adjust, y_offset_adjust = adjust_offset_coordinates(x_offset_adjust, y_offset_adjust, bound_original_image.width, bound_original_image.height, bound_adjusted_image.width, bound_adjusted_image.height, rotate_type, limb["flip_h"])
#             #                 #     x_offset_adjust, y_offset_adjust = adjust_offset_coordinates(x_offset_adjust, y_offset_adjust, bound_original_image.width, bound_original_image.height, bound_adjusted_image.width, bound_adjusted_image.height, rotate_type)

#             #                 # layer_image.paste(limb_image, (x_position + x_offset, y_position + y_offset))
#             #                 layer_image.paste(adjusted_image, (x_offset_adjust, y_offset_adjust))
                            
#             # adjusted_image, x_offset_adjust, y_offset_adjust = self.load_layer(json_data, layer_image, i, output_folder_path)
#             # layer_image.paste(adjusted_image, (x_offset_adjust, y_offset_adjust))
            
#             # sprite_sheet.paste(layer_image)
#             sprite_sheet = Image.alpha_composite(sprite_sheet, self.format_layer(i))
#             # print("Layer " + layer_names[i] + " formatted")
#             print(f"Layer {layer_data[i]['name']} formatted")
        
#         # sprite_sheet.show()
#         print("Success")
#         return sprite_sheet

#     # def export_sprite_sheet(self, path):
#     def export_sprite_sheet(self):
#         sprite_sheet_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")], initialfile= "export_" + self.json_data["header"]["name"] + "_full.png")
#         # sprite_sheet = self.format_sprite_sheet(os.path.dirname(path))
#         # sprite_sheet.save(sprite_sheet_path)

#         if sprite_sheet_path:
#             sprite_sheet_image = self.format_sprite_sheet()

#             # if (self.include_border.get()):
#                 # with Image.open(self.output_folder_path + "/" + self.json_data["header"]["border_image_path"]) as border_image:
#                     # sprite_sheet_image = Image.alpha_composite(sprite_sheet_image, border_image)

#             # self.format_sprite_sheet().save(sprite_sheet_path)
#             sprite_sheet_image.save(sprite_sheet_path)

#     # def load_layer(self, layer_info, layer_index, width, height, pose_objects):
#     #     layer_image = Image.new("RGBA", (width, height), self.color_transparent)
#     #     curr_layer_name = layer_info[layer_index]["name"]

#     #     for pose in pose_objects:
#     #         x_position = pose["x_position"]
#     #         y_position = pose["y_position"]

#     #         limb_objects = pose["limb_objects"]
#     #         for limb in limb_objects:
#     #             if limb["name"] == curr_layer_name: # does not work for images wherein different layers have the same name. either support this or prevent entirely
#     #                 # images[limb["image_index"]].open()

#     #                 with images[limb["image_index"]].open() as limb_image:
#     #                     x_offset = limb["x_offset"]
#     #                     y_offset = limb["y_offset"]
#     #                     layer_image.paste(limb_image, (x_position + x_offset, y_position + y_offset))
            
#     #     return layer_image

#     # def load_layer(self, json_data, size, layer_index, output_folder_path): # technically could just use json_data to find size
#     def format_layer(self, layer_index): # technically could just use json_data to find size
#         # output_folder_path = json_data["header"][""]
#         # pose_objects = self.json_data["pose_objects"]
#         pose_data = self.json_data["pose_data"]
#         # layer_names = self.json_data["header"]["layer_names"]
#         layer_data = self.json_data["layer_data"]
#         curr_layer_name = layer_data[layer_index]["name"]
#         layer = layer_data[layer_index]

#         layer_image = None

#         if not layer["is_border"] and not layer["is_cosmetic_only"]:

#             # images = self.json_data["images"]
#             image_data = self.json_data["image_data"]

#             # with Image.open(self.output_folder_path + "/" + self.json_data["header"]["border_image_path"]) as border_image:
#             #     size = border_image.size # might be worth saving the size as a property of self?

#             layer_image = Image.new("RGBA", self.image_size, self.color_transparent)

#             # for pose in pose_objects:
#             for pose in pose_data:
#                 x_position = pose["x_position"]
#                 y_position = pose["y_position"]

#                 # limb_objects = pose["limb_objects"]
#                 limb_data = pose["limb_data"]
#                 for limb in limb_data:
#                     if limb["name"] == curr_layer_name: # does not work for images wherein different layers have the same name. either support this or prevent entirely

#                         x_offset = limb["x_offset"]
#                         y_offset = limb["y_offset"]

#                         # with Image.open(self.output_folder_path + "/" + images[limb["image_index"]]) as limb_image:
#                         with Image.open(self.output_folder_path + "/" + image_data[limb["image_index"]]["path"]) as limb_image:
#                             adjusted_image = limb_image.copy()
#                             # could probably make everything go down 1 tab since we don't need limb_image anymore?
#                             rotate_type = None

#                             if limb["flip_h"]:
#                                 adjusted_image = adjusted_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

#                             # match limb["rotation"]:
#                             match limb["rotation_amount"]:
#                                 case 1:
#                                     rotate_type = Image.Transpose.ROTATE_90 if limb["flip_h"] else Image.Transpose.ROTATE_270
#                                 case 2:
#                                     rotate_type = Image.Transpose.ROTATE_180
#                                 case 3:
#                                     rotate_type = Image.Transpose.ROTATE_270 if limb["flip_h"] else Image.Transpose.ROTATE_90

#                             if rotate_type:
#                                 adjusted_image = adjusted_image.transpose(rotate_type)

#                             # x_offset_adjust, y_offset_adjust = x_offset + x_position, y_position + y_offset
                            
#                             # layer_image.paste(adjusted_image, (x_offset_adjust, y_offset_adjust)) # this should PROBABLY be alpha composite to avoid cutoff issues
                            
                            
#                             # stuff to prevent clipping with the different image sizes n stuff
#                             adjusted_image_bbox = adjusted_image.getbbox()
#                             if adjusted_image_bbox:
#                                 adjusted_image = adjusted_image.crop(adjusted_image_bbox)
#                                 # layer_image.paste(adjusted_image, (x_offset_adjust, y_offset_adjust))

#                                 # print(adjusted_image_bbox[0])
#                                 # print(adjusted_image_bbox[1])
#                                 # print(adjusted_image_bbox)
#                                 x_offset_adjust, y_offset_adjust = x_offset + x_position + adjusted_image_bbox[0], y_position + y_offset + adjusted_image_bbox[1]

#                                 layer_image.paste(adjusted_image, (x_offset_adjust, y_offset_adjust))
                                
                                
                                
#                                 # layer_image = Image.alpha_composite()

#                                 # return adjusted_image, x_offset_adjust, y_offset_adjust
#         else:
#             # this is assuming that there IS a search image. i dunno, i really oughta think of how to guarantee that and everything
#             layer_image_path = ((self.output_folder_path + "/") if self.json_data["header"]["paths_are_local"] else "") + layer["search_image_path"]
#             layer_image = Image.open(layer_image_path)

#         return layer_image

#     def export_layer(self):
#         # layer_index = self.json_data["header"]["layer_names"]
#         # layer_name = self.json_data["header"]["layer_names"][layer_index] # or, rather than using layername, could use string inside optionmenu?
#         layer_name = self.layer_option.get() # or, rather than using layername, could use string inside optionmenu?

#         # layer_index = self.json_data["header"]["layer_names"].index(layer_name) # will throw error if not a layer, soooo try/except?
#         layer_data = self.json_data["layer_data"]
#         layer_index = -1
#         layer = None
#         for i, l in enumerate(layer_data):
#             if l["name"] == layer_name:
#                 layer_index = i
#                 layer = l
#                 break

#         # layer_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")], initialfile= "export_" + self.json_data["header"]["name"] + "_" + layer_name + ".png")
#         layer_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")], initialfile= "export_" + self.json_data["header"]["name"] + "_" + layer_name + ".png")
        
#         # if border or cosmetic, make their respective image only. if not, 

#         if layer_path:
#             layer_image = self.format_layer(layer_index)

#             # if (self.include_border.get()):
#                 # with Image.open(self.output_folder_path + "/" + self.json_data["header"]["border_image_path"]) as border_image:
#                     # layer_image = Image.alpha_composite(layer_image, border_image)

#             layer_image.save(layer_path)

# # def adjust_offset_coordinates(
# #     x: int,
# #     y: int,
# #     orig_w: int,
# #     orig_h: int,
# #     new_w: int,
# #     new_h: int,
# #     rotation=None,
# #     # flip_h=False
# # ):
# #     """
# #     Adjusts paste coordinates for a rotated (and possibly flipped) image.

# #     Parameters:
# #         x, y: Original top-left paste coordinates
# #         orig_w, orig_h: Original size before rotation
# #         new_w, new_h: Size after rotation
# #         rotation: Image.ROTATE_90, ROTATE_180, ROTATE_270, or None
# #         flip_h: Whether the image was flipped horizontally

# #     Returns:
# #         (adjusted_x, adjusted_y)
# #     """

# #     # Horizontal flip adjustment
# #     # if flip_h:
# #     #     x = x + (orig_w - 1) - 2 * (x % orig_w)
        
# #     # Rotation adjustment
# #     if rotation == Image.ROTATE_90:
# #         x += orig_h - new_w
# #         if orig_w % 2 != orig_h % 2:
# #             x += 1 if orig_h % 2 == 0 else 0
# #             y -= 1 if orig_w % 2 == 0 else 0
# #             # x += 1
# #             # y += -1
# #             # x += 0 if orig_h % 2 == 0 else 1
# #             # y -= 0 if orig_w % 2 == 0 else 1

# #     elif rotation == Image.ROTATE_180:
# #         x += orig_w - new_w
# #         y += orig_h - new_h
# #         if orig_w % 2 != orig_h % 2:
# #             x += 1 if orig_w % 2 == 0 else 0
# #             y -= 1 if orig_h % 2 == 0 else 0
# #             # x += 1
# #             # y -= 1
# #             # x += 0 if orig_w % 2 == 0 else 1
# #             # y -= 0 if orig_h % 2 == 0 else 1

# #     elif rotation == Image.ROTATE_270:
# #         y += orig_w - new_h
# #         if orig_w % 2 != orig_h % 2:
# #             x -= 1 if orig_h % 2 == 0 else 0
# #             y += 1 if orig_w % 2 == 0 else 0
# #             # x += -1
# #             # y += 1
# #             # x -= 0 if orig_h % 2 == 0 else 1
# #             # y += 0 if orig_w % 2 == 0 else 1

# #     return x, y








# ### TODO TODO TODO: TRYING TO SEPARATE EXPORTING LAYERS AND THE ENTIRE IMAGE INTO FUNCTIONS, SO THAT THEY CAN BE SEPARATE OPTIONS!