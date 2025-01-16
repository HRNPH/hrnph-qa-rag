import json
import os
import argparse


class TagExtractor:
    @staticmethod
    def extract_tags(json_data: list) -> dict:
        try:
            tags = set()  # Use a set to avoid duplicate tags
            for item in json_data:
                tags.update(item.get("metadata", {}).get("tags", []))
            return {
                "tags": sorted(tags)
            }  # Sort the tags alphabetically for consistent output
        except Exception as e:
            return {"error": str(e)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract tags from JSON data.")
    parser.add_argument("path", type=str, help="Path to the JSON file.")
    args = parser.parse_args()

    path = args.path
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    parent_dir = os.path.dirname(path)

    with open(path, "r") as file:
        data = json.load(file)

    result = TagExtractor.extract_tags(data)

    # Save to the same path
    with open(f"{parent_dir}/tags.json", "w") as file:
        json.dump(result, file, indent=4)
