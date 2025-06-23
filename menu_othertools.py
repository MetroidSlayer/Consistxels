import traceback
import tkinter as tk
import gui_shared
from gui_shared import add_widget
from tkinter import filedialog, messagebox

from tooltip import ToolTip

from PIL import Image

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
        verify_frame.pack(padx=10, pady=10, anchor="w")

        verify_description_frame = tk.Frame(verify_frame, bg=gui_shared.bg_color)
        verify_description_frame.grid(row=0, column=0, columnspan=2, sticky="W")

        tk.Label(verify_description_frame, text="Select two images that you want to compare. The result of the comparison will be displayed. Additionally, you can save images that contain the differences between the images.",
                 bg=gui_shared.bg_color, fg=gui_shared.fg_color, justify="left", wraplength=800).pack(padx=10, pady=10, anchor="nw")
        
        verify_button_frame = tk.Frame(verify_frame, bg=gui_shared.bg_color)
        verify_button_frame.grid(row=1, column=0, padx=10, pady=(0,10), sticky="W")

        verify_button_frame.grid_columnconfigure(0, weight=1)

        self.verify_image_size = None
        self.verify_results = []

        def pick_img(entry_widget: tk.Entry): # add to gui_shared?
            path = filedialog.askopenfilename(filetypes=[("Image File", "*.png;*.jpg;*.jpeg")])
            if path:
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, path)

        self.identical_img1_path = tk.StringVar()

        img1_path_entry = add_widget(tk.Entry, verify_button_frame, {'textvariable':self.identical_img1_path}, {'text':"Enter the path to the first image, which will be compared against the second image."})
        img1_path_entry.grid(row=0, column=0, padx=10, pady=10, sticky="EW")

        img1_path_button = tk.Button(
            verify_button_frame, bg=gui_shared.button_bg, fg=gui_shared.fg_color, text="📁", command=lambda e=img1_path_entry: pick_img(e))
        img1_path_button.grid(row=0, column=1, sticky="E", padx=(0,10), pady=10)
        ToolTip(img1_path_button, "Select the first image, which will be compared against the second image.")

        self.identical_img2_path = tk.StringVar()

        img2_path_entry = add_widget(tk.Entry, verify_button_frame, {'textvariable':self.identical_img2_path}, {'text':"Enter the path to the second image, which will be compared against the first image."})
        img2_path_entry.grid(row=1, column=0, padx=10, pady=10, sticky="EW")

        img2_path_button = tk.Button(
            verify_button_frame, bg=gui_shared.button_bg, fg=gui_shared.fg_color, text="📁", command=lambda e=img2_path_entry: pick_img(e))
        img2_path_button.grid(row=1, column=1, sticky="E", padx=(0,10))
        ToolTip(img2_path_button, "Select the second image, which will be compared against the first image.")

        tk.Button(verify_button_frame, text="Compare", bg=gui_shared.button_bg, fg=gui_shared.fg_color, command=self.verify_identical
        ).grid(padx=10, pady=10, row=2, column=0, columnspan=2, sticky="EW")
        
        verify_results_frame = tk.Frame(verify_frame, bg=gui_shared.bg_color)
        verify_results_frame.grid(row=1, column=1, padx=(0,10), pady=(0,10), sticky="W")

        verify_results_header_label = tk.Label(verify_results_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Results:")
        verify_results_header_label.grid(row=0, column=0, sticky="W")

        self.verify_results_info_label = tk.Label(verify_results_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="N/A")
        self.verify_results_info_label.grid(row=1, column=0, columnspan=2, pady=(0,10), sticky="W")

        verify_results_save_label = tk.Label(verify_results_frame, bg=gui_shared.bg_color, fg=gui_shared.fg_color, text="Save results images:")
        verify_results_save_label.grid(row=2, column=0, columnspan=2, sticky="W")

        def save_verify_results_image(whichresult): # whichresult: 0 = differences in first image, 1 = differences in second image
            path = filedialog.asksaveasfilename(defaultextension=".png", title="Save image", filetypes=[("Image File", "*.png;*.jpg;*.jpeg")])
            if path:
                img = Image.new("RGBA", self.verify_image_size, (0,0,0,0))

                whichcolor = whichresult + 2
                
                for pixel_difference in self.verify_results: # 0 = x pos, 1 = y pos, 2 = img1 color, 3 = img2 color
                    img.putpixel((pixel_difference[0], pixel_difference[1]), pixel_difference[whichcolor])

                img.save(path)

        self.verify_results_save1_button = tk.Button(
            verify_results_frame, bg=gui_shared.button_bg, fg=gui_shared.fg_color, text="Image 1", command=lambda r=0: save_verify_results_image(r), state="disabled")
        self.verify_results_save1_button.grid(row=3, column=0, padx=(0,10), pady=(10,0), sticky="EW")
        ToolTip(self.verify_results_save1_button, "Save an image containing the pixels in image 1 that are different from image 2.")

        self.verify_results_save2_button = tk.Button(
            verify_results_frame, bg=gui_shared.button_bg, fg=gui_shared.fg_color, text="Image 2", command=lambda r=1: save_verify_results_image(r), state="disabled")
        self.verify_results_save2_button.grid(row=3, column=1, padx=(0,10), pady=(10,0), sticky="EW")
        ToolTip(self.verify_results_save2_button, "Save an image containing the pixels in image 2 that are different from image 1.")

    def verify_identical(self):
        img1_path = self.identical_img1_path.get()
        img2_path = self.identical_img2_path.get()
        if not img1_path or not img2_path:
            messagebox.showwarning("Warning", "Please enter paths for both images.")
            return
        
        self.verify_results = []

        try:
            with Image.open(img1_path) as img1, Image.open(img2_path) as img2:
                if img1.size != img2.size:
                    messagebox.showwarning("Warning",
                        f"Images must be the same size.\nImage 1 is {img1.size[0]}x{img1.size[1]} and Image 2 is {img2.size[0]}x{img2.size[1]}.")
                else:
                    if img1.tobytes() == img2.tobytes():
                        self.verify_results_info_label.config(text="Images are identical")
                        self.verify_results = []
                        self.verify_results_save1_button.config(state="disabled")
                        self.verify_results_save2_button.config(state="disabled")
                    else:
                        self.verify_results_info_label.config(text="Images are not identical")
                        self.verify_results = find_pixel_differences(img1, img2)
                        self.verify_results_save1_button.config(state="normal")
                        self.verify_results_save2_button.config(state="normal")
        except Exception as e:
            print("Exception:", traceback.format_exc())

def find_pixel_differences(img1, img2):
    if img1.size != img2.size:
        raise ValueError("Images are different sizes.") # good to know this is how this works

    width = img1.size[0]
    pixels1 = list(img1.getdata())
    pixels2 = list(img2.getdata())

    differences = []
    for idx, (p1, p2) in enumerate(zip(pixels1, pixels2)):
        if p1 != p2:
            x = idx % width
            y = idx // width
            differences.append((x, y, p1, p2))

    return differences