import json
import os

def combine_annotation_jsons(json_paths, output_path):
     # TODO: Complete lists
    combined_data = {
        "info": {
            "title": "Combined Dataset",
            "license": [], 
            "publication_date": [],
            "description": "Merged dataset",
            "creators": [],
            "version": [],
            "url": [],
        },
        "categories": [],
        "sounds": [],
        "annotations": []
    }

    category_map = {}
    sound_id_offset = 0
    category_id_offset = 0
    annotation_id_offset = 0

    for json_path in json_paths:
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Merge categories and update mapping
        for category in data["categories"]:
            cat_name = category["name"]
            if cat_name not in category_map:
                category_map[cat_name] = category_id_offset
                combined_data["categories"].append({
                    "id": category_id_offset,
                    "name": cat_name
                })
                category_id_offset += 1

        # Merge sounds and update IDs
        sound_id_map = {}
        for sound in data["sounds"]:
            new_sound_id = sound_id_offset
            sound_id_map[sound["id"]] = new_sound_id
            sound["id"] = new_sound_id
            combined_data["sounds"].append(sound)
            sound_id_offset += 1

        # Merge annotations with updated IDs
        for annotation in data["annotations"]:
            annotation["anno_id"] += annotation_id_offset
            annotation["sound_id"] = sound_id_map[annotation["sound_id"]]
            annotation["category_id"] = category_map[annotation["category"]]
            combined_data["annotations"].append(annotation)

        annotation_id_offset += len(data["annotations"])

    # Save merged JSON
    with open(output_path, "w", encoding="utf-8") as out_file:
        json.dump(combined_data, out_file, indent=4)

# Lista de archivos JSON a combinar
dataset_names = ["Colombia_Costa_Rica_Birds", "Southwestern_Amazon_Basin_Soundscape", "Domestic_Canari", "Enabirds"]
json_files = []
filename = ""
for dataset in dataset_names:
    json_files.append(os.path.join("data", dataset, "annotations.json"))
    filename += f"{dataset}_"
    
# Delete last underscore
if filename.endswith("_"):
    filename = filename[:-1]

output_path = os.path.join("data", "combined_datasets", f"{filename}.json")

combine_annotation_jsons(json_files, output_path)
print(f"✅ Combined dataset json saved in {output_path}")
