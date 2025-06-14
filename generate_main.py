import sys
import json
import os
import generate
from datetime import datetime

def main():
    start_time = datetime.now() # Time taken to generate is tracked and shown at the end
    # print("generatemain_gothere1")

    if len(sys.argv) < 2:
        print("Missing argument", file=sys.stderr, flush=True)
        sys.exit(1)

    input_data = json.loads(sys.argv[1])
    temp_json_path = input_data.get("val")

    if not os.path.exists(temp_json_path):
        print("Temporary .json data does not exist", file=sys.stderr, flush=True)
        sys.exit(1)

    with open(temp_json_path, 'r') as f:
        temp_json_data = json.load(f)

    os.remove(temp_json_path)

    # print(temp_json_data)
    # type = temp_json_data.get("type", "")
    type = input_data.get("type", "")
    # print(temp_json_data)
    # print(type)
    # val = temp_json_data.get("val", "")
    # print(val)
    # type = val.get("type", "")

    # print("generatemain_gothere2")

    match type:
        case "generate_pose_data":
            generate_pose_data(temp_json_data)
        case "generate_sheet_image":
            # print("generatemain_gothere3")
            generate_sheet_image(temp_json_data)
        case "generate_layer_images":
            generate_layer_images(temp_json_data)
        case "generate_external_filetype":
            generate_external_filetype(temp_json_data)
        case "generate_updated_pose_images":
            generate_updated_pose_images(temp_json_data)

    end_time = datetime.now()
    time_elapsed = end_time - start_time
    time_elapsed_seconds = int(time_elapsed.total_seconds())
    hours = time_elapsed_seconds // 3600
    minutes = (time_elapsed_seconds % 3600) // 60
    seconds = time_elapsed_seconds % 60
    formatted_time_elapsed = f"{hours:02}:{minutes:02}:{seconds:02}"
    # print("time elapsed formatted")
        
    # It's a *tad* redundant to have both update_progress and messagebox.showinfo, but I'd like to both display in the window *and* send an OS alert to the user
    # in case they tabbed out while waiting.
    # update_progress(progress_callback, 100, f"Complete! Time elapsed: {formatted_time_elapsed}")
    # print("updating progress one last time")
    # update_progress(conn, 100, "Complete!", f"Time elapsed: {formatted_time_elapsed}")
    generate.update_progress("done", 100, "Complete!", f"Time elapsed: {formatted_time_elapsed}")

def generate_pose_data(temp_json_data):
    data = temp_json_data.get("data", {})
    output_folder_path = temp_json_data.get("output_folder_path", "")

    generate.generate_all_pose_data(data, output_folder_path)

def generate_sheet_image(temp_json_data):
    # print("generatemain_gothere4")
    selected_layers = temp_json_data.get("selected_layers", []) # update comment to say update_unique_only or whatever won't work at all for this. still make it disabled at some point
    data = temp_json_data.get("data", {})
    input_folder_path = temp_json_data.get("input_folder_path", "")
    output_folder_path = temp_json_data.get("output_folder_path", "")
    # print("generatemain_gothere5")
    generate.generate_sheet_image(selected_layers, data, input_folder_path, output_folder_path)

def generate_layer_images(temp_json_data):
    selected_layers = temp_json_data.get("selected_layers", [])
    unique_only = temp_json_data.get("unique_only", False)

    data = temp_json_data.get("data", {})
    input_folder_path = temp_json_data.get("input_folder_path", "")
    output_folder_path = temp_json_data.get("output_folder_path", "")

    generate.generate_layer_images(selected_layers, unique_only, data, input_folder_path, output_folder_path)

def generate_external_filetype(temp_json_data):
    selected_layers = temp_json_data.get("selected_layers", [])

    unique_only = temp_json_data.get("unique_only", False)

    data = temp_json_data.get("data", {})
    input_folder_path = temp_json_data.get("input_folder_path", "")
    output_folder_path = temp_json_data.get("output_folder_path", "")

    generate.generate_external_filetype(selected_layers, unique_only, data, input_folder_path, output_folder_path)

def generate_updated_pose_images(temp_json_data):
    new_image_paths = temp_json_data.get("new_image_paths", [])
    data = temp_json_data.get("data", {})
    input_folder_path = temp_json_data.get("input_folder_path", "")
    # output_folder_path = temp_json_data.get("output_folder_path", "")

    generate.generate_updated_pose_images(new_image_paths, data, input_folder_path)

if __name__ == "__main__":
    main()