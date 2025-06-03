import tkinter as tk

def on_global_click(event):
    widget = event.widget.winfo_containing(event.x_root, event.y_root)
    # if widget is None or isinstance(widget, (tk.Frame, tk.Canvas, tk.Label)):
    if widget != None and isinstance(widget, (tk.Frame, tk.Canvas, tk.Label)):
        widget.winfo_toplevel().focus_set()
        # throws errors when widget is None, since it's still trying to call functions on it. would LIKE for it to defocus if none, but... there's not really a way to pass the root so that the defocus can be called? Unless there's more inside event that I'm not aware of

# might want to add constants for UI colors here???


# bg_color = "#2e2e2e"
# fg_color = "#ffffff"
# secondary_bg = "#3a3a3a"
# button_bg = "#444"