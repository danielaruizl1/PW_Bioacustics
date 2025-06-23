from BaseReader import BaseReader
import pandas as pd
import requests
import csv
import os

class WesternUnitedStatesSoundscapes(BaseReader):
    def __init__(self, data_path):
        super().__init__(data_path)
        self.sound_files_path = os.path.join(self.data_path, "soundscape_data")
        self.annotation_file = os.path.join(self.data_path, "annotations.csv")
        self.species_file = os.path.join(self.data_path, "species.csv")

    def add_dataset_info(self):
        self.annotation_creator.add_info(url="https://zenodo.org/records/7050014")

    def add_sounds(self):
        flac_files = [f for f in os.listdir(self.sound_files_path) if f.endswith('.flac')]
        latitude, longitude = (38.49,-119.95)

        for i, file_name in enumerate(flac_files):

            file_path = os.path.join(self.sound_files_path, file_name)
            duration, sample_rate = self.annotation_creator._get_duration_and_sample_rate(file_path)

            date_recorded = file_name.split('_')[2]

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
        categories_df.rename(columns={"Scientific Name": "name"}, inplace=True)
        self.annotation_creator.add_categories(categories_df)

    def add_annotations(self):
        with open(self.annotation_file, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                filename, t_min, t_max, f_min, f_max, ebirdcode = row['Filename'], float(row['Start Time (s)']), float(row['End Time (s)']), float(row['Low Freq (Hz)']), float(row['High Freq (Hz)']), row['Species eBird Code']

                sound_id = next((s["id"] for s in self.annotation_creator.data["sounds"] if filename in s["file_name_path"]), None)
                if sound_id is None:
                    continue
                
                category_match = [cat for cat in self.annotation_creator.data["categories"] if cat["Species eBird Code"] == ebirdcode]
                if not category_match:
                    continue

                category_id = category_match[0]["id"]
                category = category_match[0]["name"]

                anno_id = csv_reader.line_num - 2
                self.annotation_creator.add_annotation(
                    anno_id=anno_id, 
                    sound_id=sound_id, 
                    category_id=category_id, 
                    category=category, 
                    t_min=t_min, 
                    t_max=t_max, 
                    f_min=f_min, 
                    f_max=f_max
                )

if __name__ == "__main__":
    dataset_path = os.path.join("..","data", "Western_United_States_Soundscapes")
    reader = WesternUnitedStatesSoundscapes(dataset_path)
    reader.process_dataset()
