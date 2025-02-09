import json
import os
import argparse


class TagExtractor:
    @staticmethod
    def extract_types(json_data: list) -> dict:
        try:
            types = set()  # Use a set to avoid duplicate type
            for item in json_data:
                typ = item["metadata"]["type"]
                types.add(typ)
            return {
                "type": sorted(types)
            }  # Sort the tags alphabetically for consistent output
        except Exception as e:
            return {"error": str(e)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract types from JSON data.")
    parser.add_argument("path", type=str, help="Path to the JSON file.")
    args = parser.parse_args()

    path = args.path
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    parent_dir = os.path.dirname(path)

    with open(path, "r") as file:
        data = json.load(file)

    result = TagExtractor.extract_types(data)

    # Save to the same path
    with open(f"{parent_dir}/types.json", "w") as file:
        json.dump(result, file, indent=4)
