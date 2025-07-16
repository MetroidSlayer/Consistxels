import os
import sys
import json
from datetime import datetime

import scripts.generate.generate as generate

# Main function. Loads temporary json, starts specified generation.
def main():

    start_time = datetime.now() # Time taken to generate is tracked and shown at the end

    # Check if json is present and valid, and load it
    if len(sys.argv) < 2:
        print("Missing argument", file=sys.stderr, flush=True)
        sys.exit(1)

    input_data = None # The data provided by the user in menu_layerselect
    if "--run-generate" in sys.argv:
        input_data = json.loads(sys.argv[2])
    else:
        input_data = json.loads(sys.argv[1])

    temp_json_path = input_data.get("val")

    if not os.path.exists(temp_json_path):
        print("Temporary .json data does not exist", file=sys.stderr, flush=True)
        sys.exit(1)

    with open(temp_json_path, 'r') as f:
        temp_json_data = json.load(f)

    os.remove(temp_json_path) # Remove temp json file

    # Using the type passed in the json, choose which generation to run
    subtype = input_data.get("subtype", input_data.get("type", "")) # TODO fix preventative forgetfulness measure here, where it looks for type
    match subtype:
        case "generate_sheet_data":
            generate_sheet_data(temp_json_data)
        case "export_sheet_image":
            export_sheet_image(temp_json_data)
        case "export_layer_images":
            export_layer_images(temp_json_data)
        case "export_multilayer_file":
            export_multilayer_file(temp_json_data)
        case "update_pose_images_with_images":
            update_pose_images_with_images(temp_json_data)
        case "update_pose_images_with_multilayer_file":
            update_pose_images_with_multilayer_file(temp_json_data)

    # Generation finished, calculate time
    end_time = datetime.now()
    time_elapsed = end_time - start_time
    time_elapsed_float = time_elapsed.total_seconds()

    # generate.update_progress("done")
    update = {"type": "done", "value": 100, "time_elapsed": time_elapsed_float}
    print(json.dumps(update), flush=True)

# Generate sprite sheet data (from menu_layerselect)
def generate_sheet_data(temp_json_data):
    # Get vars
    data = temp_json_data.get("data", {})
    output_folder_path = temp_json_data.get("output_folder_path", "")

    # Generate
    generate.generate_sheet_data(data, output_folder_path)

# Generate single sprite sheet image, with all selected layers merged (from menu_loadjson)
def export_sheet_image(temp_json_data):
    # Get vars
    selected_layers = temp_json_data.get("selected_layers", [])
    data = temp_json_data.get("data", {})
    input_folder_path = temp_json_data.get("input_folder_path", "") # set to json file location? idk
    output_folder_path = temp_json_data.get("output_folder_path", "") # set to json file location? idk
    file_type = temp_json_data.get("file_type", ".png")

    # Generate
    generate.export_sheet_image(selected_layers, data, input_folder_path, output_folder_path, file_type)

# Generate multiple images, one for each selected layer (from menu_loadjson)
def export_layer_images(temp_json_data):
    # Get vars
    selected_layers = temp_json_data.get("selected_layers", [])
    pose_type = temp_json_data.get("pose_type", 0)
    data = temp_json_data.get("data", {})
    input_folder_path = temp_json_data.get("input_folder_path", "")
    output_folder_path = temp_json_data.get("output_folder_path", "")
    file_type = temp_json_data.get("file_type", ".png")

    # Generate
    # generate.generate_layer_images(selected_layers, unique_only, data, input_folder_path, output_folder_path)
    generate.export_layer_images(selected_layers, pose_type, data, input_folder_path, output_folder_path, file_type) # In theory, could still pass unique_only if it's calculated here; might work better. idk

# Generate a multi-layered file (from menu_loadjson)
def export_multilayer_file(temp_json_data):
    selected_layers = temp_json_data.get("selected_layers", [])

    pose_type = temp_json_data.get("pose_type", 0)

    data = temp_json_data.get("data", {})
    input_folder_path = temp_json_data.get("input_folder_path", "")
    output_folder_path = temp_json_data.get("output_folder_path", "")
    file_type = temp_json_data.get("file_type", ".aseprite")

    generate.export_multilayer_file(selected_layers, pose_type, data, input_folder_path, output_folder_path, file_type)

# Generate updated pose images by using inputted layers (from menu_loadjson)
def update_pose_images_with_images(temp_json_data):
    # Get vars
    image_paths = temp_json_data.get("image_paths", [])
    data = temp_json_data.get("data", {})
    input_folder_path = temp_json_data.get("input_folder_path", "")
    # selected_layers = temp_json_data.get("selected_layers", [])
    
    # Generate
    generate.update_pose_images_with_images(image_paths, data, input_folder_path)

def update_pose_images_with_multilayer_file(temp_json_data):
    # Get vars
    multilayer_file_path = temp_json_data.get("multilayer_file_path", "")
    selected_layers = temp_json_data.get("selected_layers", [])
    data = temp_json_data.get("data", {})
    input_folder_path = temp_json_data.get("input_folder_path", "")

    generate.update_pose_images_with_multilayer_file(multilayer_file_path, selected_layers, data, input_folder_path)

# Run main()
if __name__ == "__main__":
    main()