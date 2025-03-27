from BaseReader import BaseReader
import pandas as pd
import requests
import csv
import os

class ColombiaCostaRicaBirds(BaseReader):
    def __init__(self, data_path):
        super().__init__(data_path)
        self.sound_files_path = os.path.join(self.data_path, "soundscape_data")
        self.annotation_file = os.path.join(self.data_path, "annotations.csv")
        self.species_file = os.path.join(self.data_path, "species.csv")

    def add_dataset_info(self):
        self.annotation_creator.add_info(url="https://zenodo.org/records/7525349")

    def add_sounds(self):
        flac_files = [f for f in os.listdir(self.sound_files_path) if f.endswith('.flac')]
        for i, file_name in enumerate(flac_files):
            file_path = os.path.join(self.sound_files_path, file_name)
            duration, sample_rate = self.annotation_creator._get_duration_and_sample_rate(file_path)

            latitude, longitude = (5.59, -75.85) if "S01" in file_name else (10.11, -84.52) if "S02" in file_name else (None, None)
            date_recorded = file_name.split('_')[3]

            self.annotation_creator.add_sound(
                id=i,
                file_name_path= os.path.join(os.path.relpath(self.sound_files_path, self.data_path), file_name),
                duration=duration,
                sample_rate=sample_rate,
                latitude=latitude,
                longitude=longitude,
                date_recorded=date_recorded
            )

    def add_categories(self):
        categories_df = pd.read_csv(self.species_file)
        # Ensure "name" column exists; if not, use the first column
        if "name" not in categories_df.columns:
            categories_df.rename(columns={categories_df.columns[0]: "name"}, inplace=True)
        self.annotation_creator.add_categories(categories_df)

    def add_annotations(self):
        with open(self.annotation_file, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                filename, t_min, t_max, f_min, f_max, category = row['Filename'], float(row['Start Time (s)']), float(row['End Time (s)']), float(row['Low Freq (Hz)']), float(row['High Freq (Hz)']), row['Species eBird Code']

                sound_id = next((s["id"] for s in self.annotation_creator.data["sounds"] if filename in s["file_name_path"]), None)
                if sound_id is None:
                    continue

                category_match = [cat for cat in self.annotation_creator.data["categories"] if cat["name"] == category]
                if not category_match:
                    continue
                category_id = category_match[0]["id"]

                anno_id = csv_reader.line_num - 2
                self.annotation_creator.add_annotation(
                    anno_id=anno_id, 
                    sound_id=sound_id, 
                    category_id=category_id, 
                    category=category, 
                    t_min=t_min, 
                    t_max=t_max, 
                    _min=f_min, 
                    f_max=f_max
                )

if __name__ == "__main__":
    dataset_path = os.path.join("..","data", "Colombia_Costa_Rica_Birds")
    reader = ColombiaCostaRicaBirds(dataset_path)
    reader.process_dataset()
