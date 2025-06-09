import sys
import json
import os
import generate

def main():
    if len(sys.argv) < 2:
        print("Missing argument", file=sys.stderr, flush=True)
        sys.exit(1)

    temp_json_path = sys.argv[1]
    if not os.path.exists(temp_json_path):
        print("Temporary .json data does not exist", file=sys.stderr, flush=True)
        sys.exit(1)

    with open(temp_json_path, 'r') as f:
        temp_json_data = json.load(f)

    os.remove(temp_json_path)

    data = temp_json_data.get("data", {})
    path = temp_json_data.get("path", "")

    generate.generate_all(data, path)

if __name__ == "__main__":
    main()