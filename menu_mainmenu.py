import tkinter as tk
import gui_shared
from tkinter import filedialog
from gif_player import GifPlayer

# debug (MOVE to menu_othertools i think)
from PIL import Image, ImageChops


class Menu_MainMenu(tk.Frame):
    def __init__(self, master, change_menu_callback):
        super().__init__(master)

        self.configure(bg=gui_shared.bg_color) # Change bg color

        # Gif player is put inside canvas to allow clipping when window is resized to be smaller than logo
        gif_player_canvas = tk.Canvas(self, bg=gui_shared.bg_color, highlightthickness=0)
        gif_player_canvas.pack(anchor="w", padx=(10,0), pady=(10,0), fill="x")

        # Gif player containing logo, which is an animation
        gif_player = GifPlayer(gif_player_canvas, "logo anim.gif", False, 100, 8, Image.Resampling.NEAREST, bg=gui_shared.bg_color)
        
        gif_player_canvas.config(height=gif_player.winfo_reqheight()) # Change height, because otherwise it's way too tall
        gif_player_canvas.create_window((0, 0), window=gif_player, anchor="nw")

        tk.Label(self, text="A tool for more consistent pixel art", bg=gui_shared.bg_color, fg=gui_shared.fg_color).pack(anchor="w", padx=(30), pady=(0,10))

        def open_menu_with_path(menu): # Function for opening a menu and simultaneously loading a file
            path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("Json File", "*.json")])
            if path:
                change_menu_callback(menu, path)

        # Frame for boxes that contain buttons and descriptions
        content_frame = tk.Frame(self, bg=gui_shared.bg_color)
        content_frame.pack(anchor="w")

        # Generate Pose Data / menu_layerselect

        tk.Label(content_frame, text="Generate Pose Data:", bg=gui_shared.bg_color, fg=gui_shared.fg_color).pack(padx=10, pady=(10,0), anchor="w")

        generate_pose_data_frame = tk.Frame(content_frame, bg=gui_shared.bg_color, highlightthickness=2, highlightbackground=gui_shared.secondary_fg)
        generate_pose_data_frame.pack(padx=10, pady=10, anchor="w", fill="x")
        
        generate_pose_data_buttons_frame = tk.Frame(generate_pose_data_frame, bg=gui_shared.bg_color)
        generate_pose_data_buttons_frame.pack(side="left")

        tk.Button(generate_pose_data_buttons_frame, text="New", bg=gui_shared.button_bg, fg=gui_shared.fg_color,
                  command=lambda: change_menu_callback("LayerSelect")).pack(padx=10, pady=(10,0), fill="x")
        
        tk.Button(generate_pose_data_buttons_frame, text="Load layer select json", bg=gui_shared.button_bg, fg=gui_shared.fg_color,
                  command=lambda: open_menu_with_path("LayerSelect")).pack(padx=10, pady=10, fill="x")
        
        generate_pose_data_description_frame = tk.Frame(generate_pose_data_frame, bg=gui_shared.bg_color)
        generate_pose_data_description_frame.pack(side="left")

        tk.Label(generate_pose_data_description_frame, text="To get started, if you don't already have pose data for a sprite sheet, you'll need to generate it. Add and modify layers, which will be searched for any and all poses that are identical to one another. If you want to generate the same sheet more than once, you can save the selected layers and search options as a .json file and load it again later.\n\nEach unique image that's found will be exported as its own .png file. You can modify the individual pose images and see those changes reflected after exporting the sprite sheet with \"Load & Export Spritesheets with Pose Data\".",
                 bg=gui_shared.bg_color, fg=gui_shared.fg_color, justify="left", wraplength=800).pack(padx=(0,10), pady=10, anchor="nw")
        
        tk.Label(content_frame, text="Load & Export Sprite Sheet with Pose Data:",
                 bg=gui_shared.bg_color, fg=gui_shared.fg_color).pack(padx=10, pady=10, anchor="w")
        
        # Load Sheet / menu_loadjson

        load_sheet_frame = tk.Frame(content_frame, bg=gui_shared.bg_color, highlightthickness=2, highlightbackground=gui_shared.secondary_fg)
        load_sheet_frame.pack(padx=10, anchor="w", fill="x")
        
        load_sheet_buttons_frame = tk.Frame(load_sheet_frame, bg=gui_shared.bg_color, width=generate_pose_data_buttons_frame.winfo_width())
        load_sheet_buttons_frame.pack(side="left")

        tk.Button(load_sheet_buttons_frame, text="Load pose data json",
                  bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=lambda: open_menu_with_path("LoadJson")).pack(padx=10, pady=10, fill="x")
        
        load_sheet_description_frame = tk.Frame(load_sheet_frame, bg=gui_shared.bg_color)
        load_sheet_description_frame.pack(side="left")

        tk.Label(load_sheet_description_frame, text="Using the .json file that was generated alongside the pose images, load a sprite sheet. Then, choose whether to export the entire sheet as one image, or to export each layer as its own image, etc.\n\nIf a pose image has been modified, and the sheet is exported, each instance of that pose image on the original sheet will be correctly updated, so you don't have to copy-and-paste onto a gazillion different poses every time you make a tiny change.\n\nOpening each and every pose image can be time consuming, so alternatively, you can export a layer with only unique pose images, then modify them. Return to this menu with that modified sheet in order to update multiple individual pose images at once. This is probably the most efficient way of using Consistxels.",
                 bg=gui_shared.bg_color, fg=gui_shared.fg_color, justify="left", wraplength=800).pack(padx=(0,10), pady=10, anchor="nw")

        # Other tools / menu_othertools

        tk.Label(content_frame, text="Other Tools:", bg=gui_shared.bg_color, fg=gui_shared.fg_color).pack(padx=10, pady=(10,0), anchor="w")

        other_tools_frame = tk.Frame(content_frame, bg=gui_shared.bg_color, highlightthickness=2, highlightbackground=gui_shared.secondary_fg)
        other_tools_frame.pack(padx=10, pady=10, anchor="w", fill="x")
        
        other_tools_buttons_frame = tk.Frame(other_tools_frame, bg=gui_shared.bg_color)
        other_tools_buttons_frame.pack(side="left")

        tk.Button(other_tools_buttons_frame, text="Verify that two images are identical", bg=gui_shared.button_bg, fg=gui_shared.fg_color,
                  command=verify_identical).pack(padx=10, pady=(10,0), fill="x")
        
        tk.Button(other_tools_buttons_frame, text="Generate Rotated Images", bg=gui_shared.button_bg, fg=gui_shared.fg_color,
                  command=generate_rotated_images).pack(padx=10, pady=10, fill="x")
        
        other_tools_description_frame = tk.Frame(other_tools_frame, bg=gui_shared.bg_color)
        other_tools_description_frame.pack(side="left")

        tk.Label(other_tools_description_frame, text="Some other basic tools that I implemented for debugging purposes and found useful enough to keep around.",
                 bg=gui_shared.bg_color, fg=gui_shared.fg_color, justify="left", wraplength=800).pack(padx=(0,10), pady=10, anchor="nw")

        # Other description? I guess try to clean it up

        # Generate Pose Data:
        # Create, label, and order a sprite sheet's layers, and decide how the sheet will be searched.
        # Then, generate data on every pose in every layer, so that replacing every instance of a pose is much easier.
        #
        # After generating data, you can edit individual pose images. To see your changes reflected in the sprite sheet,
        # load the accompanying .json file in "Export Sprite Sheets".
        # 
        # If you don't want to edit each image individually, you
        # can generate a sheet with only unique images in "Export Sprite Sheets" - it's more convenient than opening up a
        # bunch of tiny files.
        #
        # New
        # Load .json

        # Export Sprite Sheets:
        # Using data generated in "Generate Pose Data", export 
        # Load .json

        # 

# Move these to menu_othertools
def verify_identical():
    img1_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if img1_path == None: return
    img2_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if img2_path == None: return

    with Image.open(img1_path) as img1, Image.open(img2_path) as img2:
        

        result = img1.tobytes() == img2.tobytes()

        if not result:
            difference = ImageChops.difference(img1, img2)
            result = (difference.getbbox() == None)
            if not result:
                # difference.show()
                difference_path = filedialog.asksaveasfilename(defaultextension=".png")
                try:
                    difference.save(difference_path)
                except:
                    pass

        print(result)
    
def generate_rotated_images():
    path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    with Image.open(path) as img:
        img_rot90_path = filedialog.asksaveasfilename(defaultextension=".png")
        img_rot180_path = filedialog.asksaveasfilename(defaultextension=".png")
        img_rot270_path = filedialog.asksaveasfilename(defaultextension=".png")
        img.transpose(Image.Transpose.ROTATE_90).save(img_rot90_path)
        img.transpose(Image.Transpose.ROTATE_180).save(img_rot180_path)
        img.transpose(Image.Transpose.ROTATE_270).save(img_rot270_path)

