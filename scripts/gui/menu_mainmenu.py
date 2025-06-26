import tkinter as tk
from tkinter import filedialog
from PIL import Image

import gui.gui_shared as gui_shared
from classes.gif_player import GifPlayer

# Menu containing buttons that navigate to other menus
class Menu_MainMenu(tk.Frame):
    def __init__(self, master, change_menu_callback):
        super().__init__(master) # Initialize menu's tkinter widget

        self.configure(bg=gui_shared.bg_color) # Change bg color

        # Canvas containing gif player. Exists to allow clipping when window is resized to be smaller than logo
        gif_player_canvas = tk.Canvas(self, bg=gui_shared.bg_color, highlightthickness=0)
        gif_player_canvas.pack(anchor="w", padx=(10,0), pady=(10,0), fill="x")

        # Gif player containing logo, which is an animation
        gif_player = GifPlayer(gif_player_canvas, "resources/logo anim.gif", False, 100, 8, Image.Resampling.NEAREST, bg=gui_shared.bg_color)
        
        gif_player_canvas.config(height=gif_player.winfo_reqheight()) # Change height, because otherwise it's way too tall
        gif_player_canvas.create_window((0, 0), window=gif_player, anchor="nw") # Create window containing gif

        tk.Label(self, text="A tool for more consistent pixel art", bg=gui_shared.bg_color, fg=gui_shared.fg_color).pack(anchor="w", padx=(30), pady=(0,10))

        def open_menu_with_path(menu): # Function for opening a menu and simultaneously loading a file
            path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("Json File", "*.json")])
            if path:
                change_menu_callback(menu, path)

        # Frame for boxes that contain buttons and descriptions
        content_frame = tk.Frame(self, bg=gui_shared.bg_color)
        content_frame.pack(anchor="w")

        # Generate Sprite Sheet Data / menu_layerselect

        tk.Label(content_frame, text="Generate Sprite Sheet Data:", bg=gui_shared.bg_color, fg=gui_shared.fg_color).pack(padx=10, pady=(10,0), anchor="w")

        generate_sheet_data_frame = tk.Frame(content_frame, bg=gui_shared.bg_color, highlightthickness=2, highlightbackground=gui_shared.secondary_fg)
        generate_sheet_data_frame.pack(padx=10, anchor="w", fill="x")
        
        generate_sheet_data_frame.grid_columnconfigure(0, weight=3) # For consistent formatting
        generate_sheet_data_frame.grid_columnconfigure(1, weight=1)

        generate_sheet_data_buttons_frame = tk.Frame(generate_sheet_data_frame, bg=gui_shared.bg_color)
        generate_sheet_data_buttons_frame.grid(row=0, column=0, sticky="EW")

        tk.Button(generate_sheet_data_buttons_frame, text="New", bg=gui_shared.button_bg, fg=gui_shared.fg_color,
                  command=lambda: change_menu_callback("LayerSelect")).pack(padx=10, pady=(10,0), fill="x", expand=True)
        
        tk.Button(generate_sheet_data_buttons_frame, text="Load layer select json", bg=gui_shared.button_bg, fg=gui_shared.fg_color,
                  command=lambda: open_menu_with_path("LayerSelect")).pack(padx=10, pady=10, fill="x", expand=True)
        
        generate_sheet_data_description_frame = tk.Frame(generate_sheet_data_frame, bg=gui_shared.bg_color)
        generate_sheet_data_description_frame.grid(row=0, column=1, columnspan=5, sticky="W")

        tk.Label(generate_sheet_data_description_frame, text="To get started, if you don't already have data for a sprite sheet, you'll need to generate it. Add and modify layers, which will be searched for any and all poses that are identical to one another. If you want to generate the same sheet more than once, you can save the selected layers and search options as a .json file and load it again later.\n\nEach unique image that's found will be exported as its own .png file. You can modify the individual pose images and see those changes reflected after exporting the sprite sheet with \"Load & Export Sprite Sheet with Data\".",
                 bg=gui_shared.bg_color, fg=gui_shared.fg_color, justify="left", wraplength=800).pack(padx=(0,10), pady=10, anchor="nw", fill="x")
        
        # Export Sheet / menu_exportsheet
        
        tk.Label(content_frame, text="Load & Export Sprite Sheet with Data:",
                 bg=gui_shared.bg_color, fg=gui_shared.fg_color).pack(padx=10, pady=(10,0), anchor="w")

        load_sheet_frame = tk.Frame(content_frame, bg=gui_shared.bg_color, highlightthickness=2, highlightbackground=gui_shared.secondary_fg)
        load_sheet_frame.pack(padx=10, anchor="w", fill="x")
        
        load_sheet_frame.grid_columnconfigure(0, weight=3)
        load_sheet_frame.grid_columnconfigure(1, weight=1)
        
        load_sheet_buttons_frame = tk.Frame(load_sheet_frame, bg=gui_shared.bg_color)
        load_sheet_buttons_frame.grid(row=0, column=0, sticky="EW")

        tk.Button(load_sheet_buttons_frame, text="Load sheet data json",
                  bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=lambda: open_menu_with_path("ExportSheet")).pack(padx=10, pady=10, fill="x", expand=True)
        
        load_sheet_description_frame = tk.Frame(load_sheet_frame, bg=gui_shared.bg_color)
        load_sheet_description_frame.grid(row=0, column=1, columnspan=5, sticky="W")

        tk.Label(load_sheet_description_frame, text="Using the .json file that was generated alongside the pose images, load a sprite sheet. Then, choose whether to export the entire sheet as one image, or to export each layer as its own image, etc.\n\nIf a pose image has been modified, and the sheet is exported, each instance of that pose image on the original sheet will be correctly updated, so you don't have to copy-and-paste onto a gazillion different poses every time you make a tiny change.\n\nOpening each and every pose image can be time consuming, so alternatively, you can export a layer with only unique pose images, then modify them. Return to this menu with that modified sheet in order to update multiple individual pose images at once. This is probably the most efficient way of using Consistxels.",
                 bg=gui_shared.bg_color, fg=gui_shared.fg_color, justify="left", wraplength=800).pack(padx=(0,10), pady=10, anchor="nw", fill="x")

        # Other tools / menu_othertools

        other_tools_frame = tk.Frame(content_frame, bg=gui_shared.bg_color, highlightthickness=2, highlightbackground=gui_shared.secondary_fg)
        other_tools_frame.pack(padx=10, pady=(20,10), anchor="w", fill="x")
        
        other_tools_frame.grid_columnconfigure(0, weight=3)
        other_tools_frame.grid_columnconfigure(1, weight=1)
        
        other_tools_buttons_frame = tk.Frame(other_tools_frame, bg=gui_shared.bg_color)
        other_tools_buttons_frame.grid(row=0, column=0, sticky="EW")

        tk.Button(other_tools_buttons_frame, text="Other Tools", bg=gui_shared.button_bg, fg=gui_shared.fg_color,
                  command=lambda: change_menu_callback("OtherTools")).pack(padx=10, pady=10, fill="x", expand=True)
        
        other_tools_description_frame = tk.Frame(other_tools_frame, bg=gui_shared.bg_color)
        other_tools_description_frame.grid(row=0, column=1, columnspan=5, sticky="W")

        tk.Label(other_tools_description_frame, text="Some other basic tools that I implemented for debugging purposes and found useful enough to keep around.",
                 bg=gui_shared.bg_color, fg=gui_shared.fg_color, justify="left", wraplength=800).pack(padx=(0,10), pady=10, fill="x")