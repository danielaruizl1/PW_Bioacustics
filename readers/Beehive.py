from BaseReader import BaseReader
import pandas as pd
import requests
import csv
import os

class Beehive(BaseReader):
    def __init__(self, data_path):
        super().__init__(data_path)
        self.sound_files_path = [
            os.path.join(self.data_path, "Hive1_12_06_2018"), 
            os.path.join(self.data_path, "Hive1_31_05_2018"),
            os.path.join(self.data_path, "Hive3_14_07_2017"),
            os.path.join(self.data_path, "Hive3_28_07_2017"),
            ]
        self.annotation_file = os.path.join(self.data_path, "state_labels.csv")
        self.species_file = os.path.join(self.data_path, "state_labels.csv")

    def add_dataset_info(self):
        self.annotation_creator.add_info(url="https://zenodo.org/records/2667806")

    def add_sounds(self):
        wav_files = []
        for path in self.sound_files_path:
            wav_files.extend([os.path.join(path, f) for f in os.listdir(path) if f.endswith('.wav')])
        
        for i, file_path in enumerate(wav_files):
            duration, sample_rate = self.annotation_creator._get_duration_and_sample_rate(file_path)
            date_recorded = os.path.dirname(file_path).split('_')[1:]
            date_recorded = date_recorded[2] + date_recorded[1] + date_recorded[0]

            self.annotation_creator.add_sound(
                id=i,
                file_name_path= file_path,
                duration=duration,
                sample_rate=sample_rate,
                latitude=None,
                longitude=None,
                date_recorded=date_recorded
            )

    def add_categories(self):
        df = pd.read_csv(self.species_file)
        unique_labels = df['label'].unique()
        categories_df = pd.DataFrame(unique_labels, columns=['label'])
        categories_df.rename(columns={'label': 'name'}, inplace=True)
        self.annotation_creator.add_categories(categories_df)

    def add_annotations(self):
        
        with open(self.annotation_file, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                filename, category = row['sample_name'], row['label']
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
                    t_min=0, 
                    t_max=round(self.annotation_creator.data["sounds"][sound_id]['duration'],1), 
                )

if __name__ == "__main__":
    dataset_path = os.path.join("..","data", "Beehive")
    reader = Beehive(dataset_path)
    reader.process_dataset()
