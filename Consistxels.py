import sys
import json
import subprocess
import threading
import runpy

# Global vars
gui_process : subprocess.Popen = None # Process that handles the GUI
generate_process : subprocess.Popen = None # Process that handes image/data generation
gui_has_focus : bool = True # Based on output from gui_process, prevents updates from being sent to the GUI if the window is unfocused

# Main function. Starts the GUI process and the listener thread
def main():
    # Global var
    global gui_process

    # Start GUI process
    if not getattr(sys, 'frozen', False): # If running from script:
        gui_process = subprocess.Popen(
            [sys.executable, "-m", "scripts.gui_main"],
            stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT,
            universal_newlines=True, bufsize=1,
            creationflags=subprocess.DETACHED_PROCESS
        )
    else: # If running from .exe:
        gui_process = subprocess.Popen(
            [sys.executable, "--run-gui"],
            stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT,
            universal_newlines=True, bufsize=1,
            creationflags=subprocess.DETACHED_PROCESS
        )

    # Start thread for reading GUI output
    read_gui_stdout_thread = threading.Thread(target=read_gui_stdout, daemon=True)
    read_gui_stdout_thread.start()

    read_gui_stdout_thread.join() # Join, so that main() does not end until GUI ends

    cancel_generate_process(True) # Cancel any generations that are currently going on

# Start the generate process
def start_generate_process(temp_json_filepath):
    # Global var
    global generate_process

    if not getattr(sys, 'frozen', False): # If running from script:
        generate_process = subprocess.Popen(
            [sys.executable, "-m", "scripts.generate_main", temp_json_filepath],
            stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT,
            universal_newlines=True, bufsize=1,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
        )
    else: # If running from .exe:
        generate_process = subprocess.Popen(
            [sys.executable, "--run-generate", temp_json_filepath],
            stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT,
            universal_newlines=True, bufsize=1,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
        )

    # Start thread from reading generation output
    threading.Thread(target=read_generate_stdout, daemon=True).start()

# Read GUI output
def read_gui_stdout():
    # Global vars
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
    # Global vars
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
                        if gui_has_focus: output_generate_progress(line, True)
                    case "error":
                        print(data.get("info_text", line))
                        output_generate_progress(line, True)
                        return
                    case "done":
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
    # Global var
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
    # Global var
    global generate_process

    if generate_process != None: # If there's a process, order it to close, then wait for it to close
        generate_process.terminate()
        generate_process.wait()
    elif not app_closing: # If there's not a process, but the user DELIBERATELY tried to cancel the process, something probably went wrong.
        print("Tried to cancel generate_process, but it does not exist")

# Run main
if __name__ == "__main__":
    # In order for the .exe to work, it has to call itself. These checks ensure that the created processes actually end up doing the correct thing,
    # rather than just running main() again.
    if "--run-gui" in sys.argv:
        runpy.run_module("scripts.gui_main", run_name="__main__")
    elif "--run-generate" in sys.argv:
        runpy.run_module("scripts.generate_main", run_name="__main__")
    else:
        main()