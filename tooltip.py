import tkinter as tk
import gui_shared

# A tooltip that shows up by the mouse cursor after a specified amount of time.
class ToolTip:
    def __init__(self, widget, text, force_above=False, force_left=False, delay=500, wraplength=500):
        self.widget = widget
        self.text = text
        self.delay = delay  # milliseconds
        self.wraplength = wraplength # pixels, I think
        self.tooltip_window = None
        self.id = None

        self.force_above = force_above
        self.force_left = force_left

        self.widget.bind("<Enter>", self.schedule_show)
        self.widget.bind("<Leave>", self.hide_tooltip)

    # Set the tooltip to show after a certain amount of time
    def schedule_show(self, event=None):
        self.unschedule() # If the tooltip's already scheduled, unschedule it
        self.id = self.widget.after(self.delay, self.show_tooltip)

    # Stop the tooltip from showing up
    def unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    # Show the tooltip
    def show_tooltip(self):
        if self.tooltip_window or not self.text:
            return

        # Create the tooltip window
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)

        label = tk.Label(tw, text=self.text, wraplength=self.wraplength, justify='left',
            background=gui_shared.field_bg, foreground=gui_shared.fg_color,
            highlightthickness=1, highlightbackground=gui_shared.fg_color)
        label.pack(ipadx=4, ipady=2)

        # Wait for widget geometry to be realized
        tw.update_idletasks()

        # Get tooltip size
        tooltip_width = tw.winfo_width() or 150
        tooltip_height = tw.winfo_height() or 50

        # Get mouse position and screen size
        x = self.widget.winfo_pointerx() + 20
        y = self.widget.winfo_pointery() + 20
        screen_width = self.widget.winfo_screenwidth()
        screen_height = self.widget.winfo_screenheight()

        # Adjust for screen edges
        if x + tooltip_width > screen_width:
            x = screen_width - tooltip_width - 10
        if y + tooltip_height > screen_height:
            y = screen_height - tooltip_height - 10

        if self.force_above: y = self.widget.winfo_pointery() - tooltip_height
        if self.force_left: x = self.widget.winfo_pointerx() - tooltip_width

        # Final placement
        tw.wm_geometry(f"+{x}+{y}")
    
    # Hide the tooltip
    def hide_tooltip(self, event=None):
        self.unschedule() # If the tooltip's set to show up, don't let it
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    # Unused, I think. Was going to have the tooltip follow the mouse cursor, but it looked annoying
    def move_tooltip(self, event):
        if self.tooltip_window:
            x = event.x_root + 20
            y = event.y_root + 20
            self.tooltip_window.wm_geometry(f"+{x}+{y}")