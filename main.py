import sys
import subprocess
import json
import threading

generate_process = None
gui_process = None

def main():
    global gui_process

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
        universal_newlines=True,
        creationflags=subprocess.DETACHED_PROCESS
    )

    # monitor_gui_thread = threading.Thread(target=monitor_gui, args=[gui_process], daemon=True)
    # monitor_gui_thread.start()

    read_gui_stdout_thread = threading.Thread(target=read_gui_stdout, daemon=True)
    read_gui_stdout_thread.start()

    # monitor_gui_thread.join()
    read_gui_stdout_thread.join()

    print("Main: ending")
    cancel_generate_process(True)
    # cancel any current processes! (need a way to cancel generate process, i guess)

def start_generate_process(temp_json_filepath):
    global generate_process

    generate_process = subprocess.Popen(
        [sys.executable, "-u", "generate_main.py", temp_json_filepath],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True,
        # creationflags=subprocess.CREATE_NEW_CONSOLE
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
        # creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS | subprocess.HIGH_PRIORITY_CLASS | subprocess.CREATE_BREAKAWAY_FROM_JOB,
    )

    threading.Thread(target=read_generate_stdout, daemon=True).start()

# def generate_sheet_image(temp_json_filepath):
#     global generate_process

#     pass

# def generate_layer_images(temp_json_filepath):
#     global generate_process
    
#     pass

# def generate_external_filetype(temp_json_filepath):
#     global generate_process

#     pass

# def generate_updated_pose_images(temp_json_filepath):
#     global generate_process
    
#     pass

# def monitor_gui(gui_proc):
#     while True:
#         if gui_proc.poll() is not None:
#             print("Main: GUI has exited.")
#             break
#         time.sleep(1)

def read_gui_stdout():
    global gui_process

    if gui_process != None:
        for line in gui_process.stdout:
            line = line.strip()

            try:
                data = json.loads(line)
                type = data.get("type")
                val = data.get("val")

                if type in ["generate_pose_data", "generate_sheet_image", "generate_layer_images", "generate_external_filetype", "generate_updated_pose_images"]:
                    # start_generate_process(val)
                    start_generate_process(line)
                    output_generate_progress(line, True)
                else:

                    match type:
                        # case "generate_pose_data":
                        # case "generate_pose_data", "generate_sheet_image", "generate_layer_images", "generate_external_filetype", "generate_updated_pose_images":
                        #     start_generate_process(val)
                        #     output_generate_progress(line, True)
                        # case "generate_sheet_image":
                        #     generate_sheet_image(val)
                        #     output_generate_progress(line, True)
                        # case "generate_layer_images":
                        #     generate_layer_images(val)
                        #     output_generate_progress(line, True)
                        # case "generate_external_filetype":
                        #     pass
                        # case "generate_updated_pose_images":
                        #     generate_updated_pose_images(val)
                        #     output_generate_progress(line, True)
                        case "cancel":
                            cancel_generate_process()
                            output_generate_progress(line, True)
                        case "error":
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
            except:
                print("Malformed from gui to main, in some other way:", line)

def read_generate_stdout():
    global generate_process

    if generate_process != None:
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
                        output_generate_progress(line, True)
                    case "error":
                        print(line)
                        output_generate_progress(line, True)
                        return
                    case "done":
                        # print(line)
                        output_generate_progress(line, True)
                        return
                    case "print":
                        print(info_text)
                    case _:
                        print(line)
            except json.JSONDecodeError:
                print("Malformed output from generate to main:", line)
            except:
                print("Malformed from generate to main, in some other way:", line)
            

def output_generate_progress(line, use_gui_process = False):
    global gui_process
    
    if use_gui_process and gui_process != None:
        gui_process.stdin.write(line + "\n")
        gui_process.stdin.flush()
    else: # this presumes that the status is "update", which it shouldn't presume (update: i mean not really? the value param, and any other, can be skipped entirely)
        data = json.loads(line)
        value = data.get("value")
        header_text = data.get("header_text")
        info_text = data.get("info_text")
        
        output_string = "|"
        if value: output_string += f"\tProgress: {value}%\t|"
        if header_text: output_string += f"\t{header_text}\t|"
        if info_text: output_string += f"\t{info_text}\t|"
        print(output_string)

def cancel_generate_process(app_closing = False):
    global generate_process

    if generate_process != None:
        generate_process.terminate()
        generate_process.wait()
    elif not app_closing:
        print("Tried to cancel generate_process, but it does not exist")

if __name__ == "__main__":
    main()