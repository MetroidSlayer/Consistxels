import tkinter as tk

class ToolTip:
    def __init__(self, widget, text, force_above=False, force_left=False, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay  # milliseconds
        self.tooltip_window = None
        self.id = None

        self.force_above = force_above
        self.force_left = force_left

        self.widget.bind("<Enter>", self.schedule_show)
        self.widget.bind("<Leave>", self.hide_tooltip)
        # self.widget.bind("<Motion>", self.move_tooltip)

    def schedule_show(self, event=None):
        self.unschedule()
        self.id = self.widget.after(self.delay, self.show_tooltip)

    def unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def show_tooltip(self):
        if self.tooltip_window or not self.text:
            return

        # Create the tooltip window
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)

        label = tk.Label(tw, text=self.text, justify='left',
                        background="#333", foreground="white",
                        relief='solid', borderwidth=1,
                        font=("tahoma", "9", "normal"))
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
    
    def hide_tooltip(self, event=None):
        self.unschedule()
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def move_tooltip(self, event):
        if self.tooltip_window:
            x = event.x_root + 20
            y = event.y_root + 20
            self.tooltip_window.wm_geometry(f"+{x}+{y}")