import subprocess
import threading
import sys
import json

generate_process = None
gui_process = None
gui_has_focus = True

def main():
    global gui_process

    # Start GUI process
    gui_process = subprocess.Popen(
        [sys.executable, "-u", "gui.py"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True,
        creationflags=subprocess.DETACHED_PROCESS
    )

    # Start thread for reading GUI output
    read_gui_stdout_thread = threading.Thread(target=read_gui_stdout, daemon=True)
    read_gui_stdout_thread.start()

    # Join, so that main() does not end until GUI ends
    read_gui_stdout_thread.join()

    cancel_generate_process(True) # Cancel any generations that are currently going on

def start_generate_process(temp_json_filepath):
    global generate_process

    # Start generation process, with temp_json_filepath (which contains generation details) as a parameter
    generate_process = subprocess.Popen(
        [sys.executable, "-u", "generate_main.py", temp_json_filepath],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
    )

    # Start thread from reading generation output
    threading.Thread(target=read_generate_stdout, daemon=True).start()

# Read GUI output
def read_gui_stdout():
    global gui_process
    global gui_has_focus

    if gui_process != None:
        for line in gui_process.stdout:
            line = line.strip() # Format output

            try:
                # Get output vars
                data = json.loads(line)
                type = data.get("type")
                val = data.get("val")

                # No matter the type of generation, main acts the same
                if type in ["generate_sheet_data", "generate_sheet_image", "generate_layer_images", "generate_external_filetype", "generate_updated_pose_images"]:
                    start_generate_process(line)
                    output_generate_progress(line, True)
                else:
                    match type: # Handle non-generation output
                        case "root_focus":
                            gui_has_focus = val
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

# Read generation output
def read_generate_stdout():
    global generate_process
    global gui_has_focus

    if generate_process != None:
        for line in generate_process.stdout:
            line = line.strip() # Format output

            try:
                # Get output vars
                data = json.loads(line)
                type = data.get("type")
                
                match type:
                    case "update":
                        # in order to have pretty-much-full speed while tabbed out, have some kind of polling or whatever that prevents updates (SPECIFICALLY updates)
                        # from being processed while the window is tabbed out. will be tough, might not even help much. OR have polling to only process new stuff every
                        # few milliseconds, instead of instantly, y'know how it is
                        if gui_has_focus: output_generate_progress(line, True)
                    case "error":
                        print(data.get("info_text", line))
                        output_generate_progress(line, True)
                        return
                    case "done":
                        # print(line)
                        output_generate_progress(line, True)
                        return
                    case "print":
                        print(data.get("info_text", line))
                    case _:
                        print(line)

            except json.JSONDecodeError:
                print("Malformed output from generate to main:", line)
            except:
                print("Malformed from generate to main, in some other way:", line)
            
# Either send the GUI the generate process's progress, or just print it
def output_generate_progress(line, use_gui_process = False):
    global gui_process
    
    if use_gui_process and gui_process != None:
        # Write to GUI process, send newline so it knows input is finished, flush
        gui_process.stdin.write(line + "\n")
        gui_process.stdin.flush()
    else:
        # Get vars
        data = json.loads(line)
        value = data.get("value")
        header_text = data.get("header_text")
        info_text = data.get("info_text")
        
        # Format output & print it
        output_string = "|"
        if value: output_string += f"\tProgress: {value}%\t|"
        if header_text: output_string += f"\t{header_text}\t|"
        if info_text: output_string += f"\t{info_text}\t|"
        print(output_string)

# Cancel the current generation process
def cancel_generate_process(app_closing = False):
    global generate_process

    if generate_process != None:
        generate_process.terminate()
        generate_process.wait()
    elif not app_closing:
        # It's meant to try to cancel if it doesn't exist, but only if the app is closing.
        # If the app is NOT closing, this can only run if a cancel button is pressed, and
        # cancel buttons shouldn't be available at all if a process doesn't exist
        print("Tried to cancel generate_process, but it does not exist")

if __name__ == "__main__":
    main()