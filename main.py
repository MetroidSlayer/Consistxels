# # import ctypes
# # ctypes.windll.shcore.SetProcessDpiAwareness(1)  # PER_MONITOR_AWARE

# # import tkinter as tk
# # from menu_mainmenu import Menu_MainMenu
# # from menu_layerselect import Menu_LayerSelect
# # from menu_loadjson import Menu_LoadJson

# # from shared import on_global_click
# # # import shared

# # # from generate import get_x_range
# # from generate import generate_all

# import threading

# import json
# import sys
# import tempfile
# import subprocess
# # import multiprocessing

# import os

# # class ConsistxelsApp(tk.Frame):
# #     def __init__(self, root):
# #         super().__init__()
        
# #         # self.root = root
# #         root.title("Consistxels")

# #         # for x in get_x_range(0, 10, True, False):
# #         #     print(x)

# #         # Set window attributes
# #         root.geometry("1680x768")         # window size
# #         # root.configure(bg = '#303030') # bg color

# #         self.container = tk.Frame(self)
# #         self.container.pack(fill="both", expand=True)

# #         self.bg_color = "#2e2e2e"
# #         self.fg_color = "#ffffff"
# #         self.secondary_bg = "#3a3a3a"
# #         self.button_bg = "#444"
# #         # self.button_fg = "#fff"
        

# #         # Track images and border
# #         # self.image_data = []  # List of dicts: {path, name, thumbnail, img_obj}
# #         # self.border_image = None
# #         # self.border_path = None
# #         # self.border_color = "#00007f"

# #         root.configure(bg=self.bg_color)

# #         # def on_global_click(event):
# #         #     # Get the widget under the cursor
# #         #     clicked_widget = root.winfo_containing(event.x_root, event.y_root)

# #         #     # If the widget doesn't accept focus, or is the root/frame background, clear focus
# #         #     if clicked_widget is root or isinstance(clicked_widget, tk.Frame):
# #         #         print("gothere")
# #         #         root.focus_set()
                

# #         root.bind_all("<Button-1>", on_global_click, add="+")
# #         # root.bind_class("Canvas", "<Button-1>", on_global_click, add="+")

# #         self.frames = {
# #             "Main": Menu_MainMenu(self.container, self.show_frame),
# #             "LayerSelect": Menu_LayerSelect(self.container, self.show_frame, gen),
# #             "LoadJson": Menu_LoadJson(self.container, self.show_frame)
# #         }

# #         for frame in self.frames.values():
# #             frame.place(relwidth=1, relheight=1)

# #         self.show_frame("Main")

# #         # self.after(100, self.test, (root))

# #     # def test(self, root):
# #         # print(root.state(), self.winfo_toplevel().focus_get())
# #         # self.after(100, self.test, (root))

        


# #     def show_frame(self, name):
# #         frame = self.frames[name]
# #         frame.tkraise()

# #     def on_close(self, root):
# #         # ask if want to save if curr frame has modified work

# #         self.frames["LayerSelect"].cancel_process(True)

# #         root.destroy()

# import app


# # Optional: Try this early in your script

# def main():
#     app.main(gen)
#     # print(os.environ)
#     # root = tk.Tk()
#     # app = ConsistxelsApp(root)
#     # app.pack(fill="both", expand=True)

#     # root.protocol("WM_DELETE_WINDOW", lambda r=root: app.on_close(r))

#     # root.mainloop()

# def gen(data, path, update_progress = None):
#     # threading.Thread(target=generate_all, args=(data, path, None), daemon=True).start()
#     # generate_all(data, path, None)
#     pass

#     start_process(data, path)



# def start_process(data, path):

#     temp_json_data = {"data": data, "path": path}
#     temp_json_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode='w')
#     json.dump(temp_json_data, temp_json_file)
#     temp_json_file.close()

#     # minimal_env = {
#     #     "PATH": os.environ["PATH"],
#     #     "SYSTEMROOT": os.environ.get("SYSTEMROOT", "C:\\Windows"),
#     #     "SystemDrive": os.environ.get("SystemDrive", "C:"),
#     #     "TEMP": os.environ.get("TEMP", "C:\\Temp"),
#     #     "TMP": os.environ.get("TMP", "C:\\Temp"),
#     # }

#     # process = subprocess.Popen(
#     #     [sys.executable, "generate_worker.py", temp_json_file.name],
#     #     stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
#     #     text=True,
#     #     creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS | subprocess.HIGH_PRIORITY_CLASS
#     #     # creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS | subprocess.HIGH_PRIORITY_CLASS | subprocess.CREATE_NEW_CONSOLE
#     #     # creationflags= subprocess.CREATE_NEW_CONSOLE | subprocess.HIGH_PRIORITY_CLASS
#     #     # env=minimal_env
#     # )

#     # subprocess.Popen(["generate_pose_data.bat", temp_json_file.name], shell=True)

#     # cmd = (
#     #     'cmd.exe',
#     #     '/c',
#     #     'start',
#     #     '""',  # Window title
#     #     '/HIGH',
#     #     'python',
#     #     'generate_worker.py',
#     #     temp_json_file.name
#     # )

#     # subprocess.Popen(
#     #     cmd,
#     #     shell=False,
#     #     creationflags=subprocess.CREATE_NEW_CONSOLE
#     # )


#     json_path = temp_json_file.name.replace("\\", "/")
#     # print(json_path)

#     # print(os.path.abspath(temp_json_file))

#     # script_path = os.path.abspath("generate_worker.py")
#     # python_exe = sys.executable

#     # # Correct quoting and escaping: entire start command must be one string
#     # start_cmd = f'start "" /HIGH "{python_exe}" "{script_path}" "{json_path}"'

#     # # Use shell=True now, because we are manually building the full command line
#     # subprocess.Popen(start_cmd, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)

#     exe_path = os.path.abspath("dist/generate_worker.exe")
#     subprocess.Popen(
#         [exe_path, json_path],
#         creationflags= subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.HIGH_PRIORITY_CLASS
#     )

#     # most_recent_line = None

#     # threading.Thread(target=read_process_stdout, args=[process], daemon=True).start()

# # def read_process_stdout(process):
#     # for line in process.stdout:
#     #     line = line.strip()
#     #     try:

#     #         data = json.loads(line)
#     #         status = data.get("status")
#     #         header_text = data.get("header_text")
#     #         info_text = data.get("info_text")
#     #         value = data.get("value")
                
#     #         match status:
#     #             case "update":
#     #                 print(line)
#     #             case "error":
#     #                 print(line)
#     #                 return
#     #             case "done":
#     #                 print(line)
#     #                 return
#     #             case "print":
#     #                 print(info_text)
#     #     except json.JSONDecodeError:
#     #         print("Malformed output:", line)

# # run main
# if __name__ == "__main__":
#     main()

# # import asyncio
# # import tkinter as tk
# # from tkinter import ttk
# # import sys
# # import json

# # from datetime import datetime

# # class App:
# #     def __init__(self, root):
# #         self.root = root
# #         self.root.title("Main Window")
# #         self.button = tk.Button(root, text="Start Processing", command=self.start_processing)
# #         self.button.pack(padx=20, pady=20)
# #         self.process = None
# #         self.progress_win = None
# #         self.progress_var = tk.IntVar()

# #         # Setup asyncio loop integration with tkinter
# #         self.loop = asyncio.get_event_loop()
# #         self._asyncio_loop_step()

# #     def _asyncio_loop_step(self):
# #         """Run asyncio event loop for a short step, then reschedule."""
# #         try:
# #             self.loop.call_soon(self.loop.stop)
# #             self.loop.run_forever()
# #         except Exception as e:
# #             print("Asyncio loop exception:", e)
# #         self.root.after(50, self._asyncio_loop_step)

# #     def start_processing(self):
# #         if self.process:
# #             return  # Already running
# #         self.open_progress_window()
# #         asyncio.ensure_future(self.run_subprocess())

# #     def open_progress_window(self):
# #         self.progress_win = tk.Toplevel(self.root)
# #         self.progress_win.title("Processing...")
# #         ttk.Label(self.progress_win, text="Progress:").pack(padx=10, pady=10)
# #         progress_bar = ttk.Progressbar(self.progress_win, orient="horizontal", length=300, mode="determinate", maximum=100, variable=self.progress_var)
# #         progress_bar.pack(padx=10, pady=10)
# #         cancel_button = tk.Button(self.progress_win, text="Cancel", command=self.cancel_process)
# #         cancel_button.pack(padx=10, pady=10)

# #     async def run_subprocess(self):
# #         start_time = datetime.now() # Time taken to generate is tracked and shown at the end

# #         cmd = [sys.executable, "generate.py"]
# #         # cmd = [sys.executable, "generate_worker.py"]
# #         self.process = await asyncio.create_subprocess_exec(
# #             *cmd,
# #             stdout=asyncio.subprocess.PIPE,
# #             stderr=asyncio.subprocess.PIPE
# #         )

# #         try:
# #             while True:
# #                 line = await self.process.stdout.readline()
# #                 if not line:
# #                     break
# #                 progress = int(line.decode().strip())
# #                 self.progress_var.set(progress)
# #                 self.root.update_idletasks()

# #                 # data = json.loads(line)
# #                 # # status = data.get("status")
# #                 # # header_text = data.get("header_text")
# #                 # # info_text = data.get("info_text")
# #                 # value = data.get("value")
                    
# #                 # self.progress_var.set(value)
# #                 # self.root.update_idletasks()
                
# #                 # match status:
# #                 #     case "update":
# #                 #         print(line)
# #                 #     case "error":
# #                 #         print(line)
# #                 #         return
# #                 #     case "done":
# #                 #         print(line)
# #                 #         return
# #                 #     case "print":
# #                 #         print(info_text)
                

# #             await self.process.wait()
# #         except asyncio.CancelledError:
# #             if self.process:
# #                 self.process.kill()
# #         finally:
# #             self.process = None
# #             if self.progress_win:
# #                 self.progress_win.destroy()
# #                 self.progress_win = None

# #                 end_time = datetime.now()
# #                 time_elapsed = end_time - start_time
# #                 time_elapsed_seconds = int(time_elapsed.total_seconds())
# #                 hours = time_elapsed_seconds // 3600
# #                 minutes = (time_elapsed_seconds % 3600) // 60
# #                 seconds = time_elapsed_seconds % 60
# #                 formatted_time_elapsed = f"{hours:02}:{minutes:02}:{seconds:02}"
# #                 print(formatted_time_elapsed)

# #     def cancel_process(self):
# #         if self.process:
# #             self.process.terminate()

# # if __name__ == "__main__":
# #     root = tk.Tk()
# #     app = App(root)
# #     root.mainloop()

# # import asyncio
# # import tkinter as tk
# # from tkinter import ttk
# # import sys
# # import os

# # class App:
# #     def __init__(self, root):
# #         self.root = root
# #         self.root.title("Prime Generator")

# #         self.button = tk.Button(root, text="Start Prime Calculation", command=self.start_processing)
# #         self.button.pack(padx=20, pady=20)

# #         self.process = None
# #         self.progress_win = None
# #         self.progress_var = tk.IntVar()

# #         # Set up asyncio integration with tkinter's mainloop
# #         self.loop = asyncio.get_event_loop()
# #         self._run_asyncio_loop_step()

# #     def _run_asyncio_loop_step(self):
# #         """Run asyncio event loop for a short step, then reschedule."""
# #         try:
# #             self.loop.call_soon(self.loop.stop)
# #             self.loop.run_forever()
# #         except Exception as e:
# #             print("Asyncio loop error:", e)
# #         self.root.after(50, self._run_asyncio_loop_step)

# #     def start_processing(self):
# #         if self.process:
# #             return  # Already running
# #         self.open_progress_window()
# #         asyncio.ensure_future(self.run_subprocess())

# #     def open_progress_window(self):
# #         self.progress_win = tk.Toplevel(self.root)
# #         self.progress_win.title("Generating Primes...")
# #         ttk.Label(self.progress_win, text="Progress:").pack(padx=10, pady=10)

# #         progress_bar = ttk.Progressbar(
# #             self.progress_win, orient="horizontal", length=300, mode="determinate",
# #             maximum=100, variable=self.progress_var
# #         )
# #         progress_bar.pack(padx=10, pady=10)

# #         cancel_button = tk.Button(self.progress_win, text="Cancel", command=self.cancel_process)
# #         cancel_button.pack(padx=10, pady=10)

# #     async def run_subprocess(self):
# #         cmd = [sys.executable, "generate.py"]
# #         env = os.environ.copy()

# #         self.process = await asyncio.create_subprocess_exec(
# #             *cmd,
# #             stdout=asyncio.subprocess.PIPE,
# #             stderr=asyncio.subprocess.PIPE,
# #             env=env
# #         )

# #         try:
# #             while True:
# #                 line = await self.process.stdout.readline()
# #                 if not line:
# #                     break
# #                 try:
# #                     progress = int(line.decode().strip())
# #                     self.progress_var.set(progress)
# #                     self.root.update_idletasks()
# #                 except ValueError:
# #                     print("Invalid output:", line.decode().strip())
            
# #             await self.process.wait()

# #         except asyncio.CancelledError:
# #             if self.process:
# #                 self.process.kill()
# #         finally:
# #             if self.progress_win:
# #                 self.progress_win.destroy()
# #                 self.progress_win = None
# #             self.process = None

# #     def cancel_process(self):
# #         if self.process:
# #             self.process.terminate()

# # if __name__ == "__main__":
# #     root = tk.Tk()
# #     app = App(root)
# #     root.mainloop()

# import gui
import sys
import subprocess
import json
import threading
import time

def main():
    gui_process = subprocess.Popen(
        # [sys.executable, "gui.py"],
        # stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        # creationflags=subprocess.DETACHED_PROCESS
        # # creationflags=subprocess.CREATE_NEW_CONSOLE
        [sys.executable, "-u", "gui.py"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True,  # for line-by-line reading
        creationflags=subprocess.DETACHED_PROCESS
    )

    # generate_process = subprocess.Popen(
    #     [sys.executable, "-u", "generate_worker.py"],
    #     # stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    #     text=True,
    #     creationflags=subprocess.CREATE_NEW_CONSOLE
    #     # creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
    #     # creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS | subprocess.HIGH_PRIORITY_CLASS | subprocess.CREATE_BREAKAWAY_FROM_JOB,
    #     # env=env
    # )
    # monitor_gui_thread = threading.Thread(target=monitor_gui, args=[gui_process], daemon=True)
    # monitor_gui_thread.start()

    read_gui_stdout_thread = threading.Thread(target=read_gui_stdout, args=[gui_process], daemon=True)
    read_gui_stdout_thread.start()

    # monitor_gui_thread.join()
    read_gui_stdout_thread.join()

    print("Main: ending")

    # cancel any current processes! (need a way to cancel generate process, i guess)

    # threading.Thread(target=read_process_stdout, args=[generate_process], daemon=True).start()

    # SO, it seems that the stuff like generate_all() (THIS one, not the one in generate.py) are not running because this process is closing early. Basically, we gotta keep
    # it open, and then we just gotta figure out how to wire it all together.
    # input("test")

    # try:
    #     while True:
    #         # Check if the GUI subprocess is still running
    #         retcode = gui_process.poll()
    #         if retcode is not None:
    #             print(f"Main: GUI exited with code {retcode}. Shutting down.")
    #             break
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     print("Main: Interrupted. Terminating GUI.")
    #     gui_process.terminate()
    #     # terminate generate subprocess too if necessary

def generate_all(temp_json_filepath, gui_process):
    # print("got to generate_all")

    generate_process = subprocess.Popen(
        [sys.executable, "-u", "generate_worker.py", temp_json_filepath],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True,
        # creationflags=subprocess.CREATE_NEW_CONSOLE
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
        # creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS | subprocess.HIGH_PRIORITY_CLASS | subprocess.CREATE_BREAKAWAY_FROM_JOB,
        # env=env
    )

    threading.Thread(target=read_generate_stdout, args=[generate_process, gui_process], daemon=True).start()

# def monitor_gui(gui_proc):
#     while True:
#         if gui_proc.poll() is not None:
#             print("Main: GUI has exited.")
#             break
#         time.sleep(1)

def read_gui_stdout(gui_process):
    for line in gui_process.stdout:
        # print("gothere", line)
        line = line.strip()
        # print("gothere2", line)

        try:
            # print("gothere3", line)

            data = json.loads(line)
            type = data.get("type")
            val = data.get("val")

            # print("gothere4", type, val)
                
            # print(line)
            match type:
                case "generate":
                    generate_all(val, gui_process)
                    output_generate_progress(line, gui_process)
                case "cancel":
                    pass # TODO cancel
                    # cancel_generate_process() # will need SOME way to store the generate process, methinks
                case "error":
                    # print(line)
                    print(f"Error in gui\n{val}")
                    return
                case "done":
                    print(line)
                    return
                case "print":
                    print(val)
                case _:
                    print(line)

        except json.JSONDecodeError:
            print("Malformed output from gui to main:", line)

def read_generate_stdout(generate_process, gui_process = None):
    for line in generate_process.stdout:
        line = line.strip()

        try:

            data = json.loads(line)
            type = data.get("type")
            # header_text = data.get("header_text")
            info_text = data.get("info_text")
            # value = data.get("value")
            
            match type:
                case "update":
                    # print(line)
                    # in order to have pretty-much-full speed while tabbed out, have some kind of polling or whatever that prevents updates (SPECIFICALLY updates)
                    # from being processed while the window is tabbed out. will be tough, might not even help much. OR have polling to only process new stuff every
                    # few milliseconds, instead of instantly, y'know how it is
                    output_generate_progress(line, gui_process)
                case "error":
                    print(line)
                    output_generate_progress(line, gui_process)
                    return
                case "done":
                    print(line)
                    output_generate_progress(line, gui_process)
                    return
                case "print":
                    print(info_text)
                case _:
                    print(line)
        except json.JSONDecodeError:
            print("Malformed output from generate to main:", line)

def output_generate_progress(line, gui_process = None):
    
    if gui_process != None:
        # print("got to gui_process.stdin.write(line)")
        # print(line)
        gui_process.stdin.write(line + "\n")
        gui_process.stdin.flush()
    else:
        data = json.loads(line)
        value = data.get("value")
        header_text = data.get("header_text")
        info_text = data.get("info_text")
        
        output_string = ""
        if value: output_string += f"Progress: {value}%\t|\t"
        if header_text: output_string += f"{header_text}\t|\t"
        if info_text: output_string += f"{info_text}\t|"
        print(output_string)

if __name__ == "__main__":
    main()