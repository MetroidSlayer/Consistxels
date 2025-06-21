import tkinter as tk
from tkinter import messagebox
from PIL import Image

from tooltip import ToolTip

# Style info. Eventually, this will be modifiable by the user, probably
bg_color = "#2e2e2e"
fg_color = "#ffffff"

secondary_bg = "#3a3a3a"
secondary_fg = "#6a6a6a"

button_bg = "#444444"
field_bg = "#222222"

danger_fg = "#dd5555"

warning_bg = "#ffff6c"
warning_fg = "#1B1B1B"

# Add widget
# def add_widget(widget_class, master, config_args = {}, placement_func = None, placement_args = {}, tooltip_args = None):
def add_widget(widget_class, master, config_args = {}, tooltip_args = None):

    widget = widget_class(master)

    match widget_class:
        # case tk.Label:
        #     if not config_args.get("bg"): config_args.update({"bg": bg_color})
        #     if not config_args.get("fg"): config_args.update({"fg": fg_color})
        case tk.Entry:
            if not config_args.get("bg"): config_args.update({"bg": field_bg})
            if not config_args.get("fg"): config_args.update({"fg": fg_color})

            # For changing color while focused
            widget.bind("<FocusIn>", on_entry_FocusIn, add='+')
            widget.bind("<FocusOut>", on_entry_FocusOut, add='+')
        # case tk.Button:
        #     if not config_args.get("bg"): config_args.update({"bg": button_bg})
        #     if not config_args.get("fg"): config_args.update({"fg": fg_color})
        # case tk.OptionMenu:
        #     if not config_args.get("bg"): config_args.update({"bg": field_bg})
        #     if not config_args.get("fg"): config_args.update({"fg": fg_color})
        #     if not config_args.get("activebackground"): config_args.update({"activebackground": bg_color})
        #     if not config_args.get("activeforeground"): config_args.update({"activeforeground": fg_color})
        #     if not config_args.get("anchor"): config_args.update({"anchor": "w"})
        #     if not config_args.get("justify"): config_args.update({"justify": "left"})
        #     if not config_args.get("highlightthickness"): config_args.update({"highlightthickness": 1})
        #     if not config_args.get("highlightbackground"): config_args.update({"highlightbackground": secondary_fg})
        #     if not config_args.get("bd"): config_args.update({"bd": 0})
        #     if not config_args.get("relief"): config_args.update({"relief": "flat"})

        #     # Presumably, I'm not ever gonna wanna change this manually
        #     widget["menu"].configure(bg=field_bg, fg=fg_color, activebackground=secondary_bg, activeforeground=fg_color)
        # case tk.Frame:
        #     if not config_args.get("bg"): config_args.update({"bg": bg_color})
            # print(config_args)
        # case tk.PanedWindow:
        #     # if widget_class != tk.Frame:
        #         if not config_args.get("bg"): config_args.update({"bg": field_bg})
        #         if not config_args.get("opaqueresize"): config_args.update({"opaqueresize": False})
        #         if not config_args.get("sashrelief"): config_args.update({"sashrelief": "flat"})
        #         if not config_args.get("sashwidth"): config_args.update({"sashwidth": 16})
        #         if not config_args.get("bd"): config_args.update({"bd": 0})
            
        # case _:
        #     # will throw an error if bg does not exist for that widget! so maybe do smth else idk
        #     if not config_args.get("bg"): config_args.update({"bg": bg_color})
    
    # # Temporarily create a dummy widget to fetch allowed option keys
    # dummy = widget_class(master)
    # valid_keys = dummy.keys()
    # dummy.destroy()

    # # Filter out invalid widget options
    # filtered_widget_kwargs = {k: v for k, v in config_args.items() if k in valid_keys}

    # # Create the actual widget
    # # (WOULDN'T HAVE WORKED ANYWAY, as I already created widget above)
    # widget = widget_class(master, **filtered_widget_kwargs)

    # if widget_class == tk.Frame and config_args.get("opaqueresize") != None:
    #     raise Exception

    widget.configure(**config_args)

    # if placement_func != None:
    #     getattr(widget, placement_func)(**placement_args)

    if tooltip_args != None:
        if tooltip_args.get('text'): tooltip_args["text"] = tooltip_args["text"].strip()
        ToolTip(widget, **tooltip_args)
    
    return widget

def on_entry_FocusIn(event):
    event.widget.configure(bg=secondary_bg)
    
def on_entry_FocusOut(event):
    event.widget.configure(bg=field_bg)

# If something is focused, and anywhere on the window is clicked, unfocus (just makes it feel smoother)
def on_global_click(event):
    widget = event.widget.winfo_containing(event.x_root, event.y_root)
    # if widget is None or isinstance(widget, (tk.Frame, tk.Canvas, tk.Label)):
    if widget != None and isinstance(widget, (tk.Frame, tk.Canvas, tk.Label)):
        widget.winfo_toplevel().focus_set()
        # throws errors when widget is None, since it's still trying to call functions on it. would LIKE for it to defocus if none, but... there's not really a way to pass the root so that the defocus can be called? Unless there's more inside event that I'm not aware of

# Recursively binds the widget, its children, and its grandchildren, etc.
def bind_event_to_all_children(widget, sequence, func):
    widget.bind(sequence, func)
    for child in widget.winfo_children():
        bind_event_to_all_children(child, sequence, func)

# Funcs for checking various common things in the menus

# Get the size of the image at the path and return it
def get_image_size(image_path: str) -> tuple[int, int]:
    try:
        with Image.open(image_path) as image:
            return image.size
    except AttributeError: # TODO TEST
        return None

# # Compare one image against a desired size
# def compare_image_size(image_path, desired_size) -> bool:
#     pass

# # Compare a list of images against a desired size
# def compare_all_image_sizes() -> bool:
#     pass

def get_all_image_sizes(image_paths: list[str]) -> list[tuple[int, int]]:
    sizes = []
    for image_path in image_paths:
        sizes.append(get_image_size(image_path))
    return sizes

# Check all sizes, format output for user to view sizes
def warn_image_sizes(category_name_list: list[str], category_paths_list: list[list[str]], accept_different_sizes: bool = False) -> bool:
    lastsize = None
    matching_sizes = True
    # throw error if length of category_name and category_paths do not match?
    category_sizes_list = []
    
    for i in range(len(category_name_list)):
        category_sizes_list.append(get_all_image_sizes(category_paths_list[i]))
    
        for size in category_sizes_list[i]:
            if lastsize != None:
                if size and size != lastsize:
                    matching_sizes = False
                    break
            else:
                lastsize = size
    
    if not matching_sizes:
        size_output = ""
        for i in range(len(category_sizes_list[0])):
            curr_output = f"Layer {i + 1}:\n"
            # size_output += f"Layer {i + 1}:\n"
            added_any = False
            for j, name in enumerate(category_name_list):
                curr_size = category_sizes_list[j][i]
                if curr_size != None:
                    # size_output += f"{name}: {curr_size[0]}x{curr_size[1]}\n"
                    curr_output += f"{name}: {curr_size[0]}x{curr_size[1]}\n"
                    added_any = True
            # if not added_any: size_output += "(No images in this layer)\n"
            # if not added_any: curr_output = ""
            # size_output += "\n"
            # else: curr_output += "\n"
            if added_any: size_output += curr_output + "\n"

        if not accept_different_sizes:
            messagebox.showwarning("Warning!", f"Images cannot be different sizes.\nCurrent image sizes:\n\n{size_output}")
            return False
        else:
            return messagebox.askyesno("Warning!",
                f"Some images are different sizes. Performing operations on images of different sizes may lead to unintended results. Continue anyway?\nCurrent image sizes:\n\n{size_output}")
    return True


# Warn about possibly overwriting data
def warn_overwrite() -> bool:
    return messagebox.askokcancel("Warning!", "The selected folder is not empty. If you export to this folder, you may overwrite existing data.")