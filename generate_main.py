import os
import sys
import json
from datetime import datetime

import generate

# Main function. Loads temporary json, starts specified generation
def main():
    start_time = datetime.now() # Time taken to generate is tracked and shown at the end

    # Check if json is present and valid, and load it
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

    os.remove(temp_json_path) # Remove temp json file

    # Using the type passed in the json, choose which generation to run
    type = input_data.get("type", "")

    match type:
        case "generate_sheet_data":
            generate_sheet_data(temp_json_data)
        case "generate_sheet_image":
            generate_sheet_image(temp_json_data)
        case "generate_layer_images":
            generate_layer_images(temp_json_data)
        case "generate_external_filetype":
            generate_external_filetype(temp_json_data)
        case "generate_updated_pose_images":
            generate_updated_pose_images(temp_json_data)

    # Generation finished, calculate time
    end_time = datetime.now()
    time_elapsed = end_time - start_time
    time_elapsed_seconds = int(time_elapsed.total_seconds())
    hours = time_elapsed_seconds // 3600
    minutes = (time_elapsed_seconds % 3600) // 60
    seconds = time_elapsed_seconds % 60
    formatted_time_elapsed = f"{hours:02}:{minutes:02}:{seconds:02}"

    # Output that the generation has finished.
    generate.update_progress("done", 100, "Complete!", f"Time elapsed: {formatted_time_elapsed}")

# Generate sprite sheet data (from menu_layerselect)
def generate_sheet_data(temp_json_data):
    # Get vars
    data = temp_json_data.get("data", {})
    output_folder_path = temp_json_data.get("output_folder_path", "")

    # Generate
    generate.generate_sheet_data(data, output_folder_path)

# Generate single sprite sheet image, with all selected layers merged (from menu_loadjson)
def generate_sheet_image(temp_json_data):
    # Get vars
    selected_layers = temp_json_data.get("selected_layers", [])
    data = temp_json_data.get("data", {})
    input_folder_path = temp_json_data.get("input_folder_path", "")
    output_folder_path = temp_json_data.get("output_folder_path", "")

    # Generate
    generate.generate_sheet_image(selected_layers, data, input_folder_path, output_folder_path)

# Generate multiple images, one for each selected layer (from menu_loadjson)
def generate_layer_images(temp_json_data):
    # Get vars
    selected_layers = temp_json_data.get("selected_layers", [])
    unique_only = temp_json_data.get("unique_only", False)
    data = temp_json_data.get("data", {})
    input_folder_path = temp_json_data.get("input_folder_path", "")
    output_folder_path = temp_json_data.get("output_folder_path", "")

    # Generate
    generate.generate_layer_images(selected_layers, unique_only, data, input_folder_path, output_folder_path)

# Generate a multi-layered file (from menu_loadjson)
def generate_external_filetype(temp_json_data):
    selected_layers = temp_json_data.get("selected_layers", [])

    unique_only = temp_json_data.get("unique_only", False)

    data = temp_json_data.get("data", {})
    input_folder_path = temp_json_data.get("input_folder_path", "")
    output_folder_path = temp_json_data.get("output_folder_path", "")

    generate.generate_external_filetype(selected_layers, unique_only, data, input_folder_path, output_folder_path)

# Generate updated pose images by using inputted layers (from menu_loadjson)
def generate_updated_pose_images(temp_json_data):
    # Get vars
    new_image_paths = temp_json_data.get("new_image_paths", [])
    data = temp_json_data.get("data", {})
    input_folder_path = temp_json_data.get("input_folder_path", "")
    
    # Generate
    generate.generate_updated_pose_images(new_image_paths, data, input_folder_path)

# Run main()
if __name__ == "__main__":
    main()