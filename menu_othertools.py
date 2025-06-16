import tkinter as tk
import gui_shared
from tkinter import filedialog

from tooltip import ToolTip

# debug (MOVE to menu_othertools i think)
from PIL import Image, ImageChops

class Menu_OtherTools(tk.Frame):
    def __init__(self, master, change_menu_callback):
        super().__init__(master)

        self.configure(bg=gui_shared.bg_color) # Change bg color
        
        self.setup_ui(change_menu_callback)
    
    def setup_ui(self, change_menu_callback):

        # Header
        self.header = tk.Frame(self, bg=gui_shared.bg_color)
        self.header.pack(fill="x", padx=2)

        # Back button
        self.back_button = tk.Button(self.header, text="Back to Main Menu", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=lambda: change_menu_callback("Main"))
        self.back_button.pack(side="right", padx=10, pady=10)
        ToolTip(self.back_button, "...Come on, this one is self explanatory.", False, True, 2000)

        # Main frame
        self.main_frame = tk.Frame(self, bg=gui_shared.bg_color)
        self.main_frame.pack(fill="both", expand=True)

        
        tk.Label(self.main_frame, text="Verify that two images are identical:", bg=gui_shared.bg_color, fg=gui_shared.fg_color).pack(padx=10, pady=(10,0), anchor="w")

        verify_frame = tk.Frame(self.main_frame, bg=gui_shared.bg_color, highlightthickness=2, highlightbackground=gui_shared.secondary_fg)
        verify_frame.pack(padx=10, pady=10, anchor="w", fill="x")
        
        verify_button_frame = tk.Frame(verify_frame, bg=gui_shared.bg_color)
        verify_button_frame.pack(side="left")

        tk.Button(verify_button_frame, text="Select images", bg=gui_shared.button_bg, fg=gui_shared.fg_color,
                  command=verify_identical).pack(padx=10, pady=(10,0), fill="x")
        
        # tk.Button(verify_button_frame, text="Generate Rotated Images", bg=gui_shared.button_bg, fg=gui_shared.fg_color,
        #           command=generate_rotated_images).pack(padx=10, pady=10, fill="x")
        
        verify_description_frame = tk.Frame(verify_frame, bg=gui_shared.bg_color)
        verify_description_frame.pack(side="left")

        # TODO REWORK DESC FOR BETTER FUNCTION
        tk.Label(verify_description_frame, text="A file dialog will pop up; select the first image. A second will pop up right after; select the second image. If NOTHING happens from here, the images ARE identical. If ANOTHER file dialog pops up, SAVE the image; this shows the differences between the images.",
                 bg=gui_shared.bg_color, fg=gui_shared.fg_color, justify="left", wraplength=800).pack(padx=(0,10), pady=10, anchor="nw")

# TODO TODO TODO make work better for users specifically
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
    
# def generate_rotated_images():
#     path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
#     with Image.open(path) as img:
#         img_rot90_path = filedialog.asksaveasfilename(defaultextension=".png")
#         img_rot180_path = filedialog.asksaveasfilename(defaultextension=".png")
#         img_rot270_path = filedialog.asksaveasfilename(defaultextension=".png")
#         img.transpose(Image.Transpose.ROTATE_90).save(img_rot90_path)
#         img.transpose(Image.Transpose.ROTATE_180).save(img_rot180_path)
#         img.transpose(Image.Transpose.ROTATE_270).save(img_rot270_path)

