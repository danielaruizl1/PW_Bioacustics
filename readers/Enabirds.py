from BaseReader import BaseReader
import pandas as pd
import os
import csv

class EnabirdsReader(BaseReader):
    def __init__(self, data_path):
        super().__init__(data_path)
        self.sound_files_path = os.path.join(self.data_path, "wav_Files")
        self.annotation_files_path = os.path.join(self.data_path, "annotation_Files")

    def add_dataset_info(self):
        # TODO: Check if we can get metadata from dryad as with zenodo
        self.annotation_creator.add_info(
            title = "Enabirds",
            license = "CC0-1.0",
            url = "https://datadryad.org/stash/dataset/doi:10.5061/dryad.d2547d81z",
            )

    def add_categories(self):
        unique_categories = set()
        annotation_files = []
        for root, _, files in os.walk(self.annotation_files_path):
            for file in files:
                if file.endswith(".txt"):
                    annotation_files.append(os.path.join(root, file))
        
        for file_path in annotation_files:
            with open(file_path, mode='r') as file:
                lines = file.readlines()
                header = [h.strip() for h in lines[0].split('\t')]
                
                if 'Species' not in header:
                    continue
                
                reader = csv.DictReader(lines[1:], delimiter='\t', fieldnames=header)
                for row in reader:
                    unique_categories.add(row['Species'])
        
        categories_df = pd.DataFrame({'name': list(unique_categories)})
        self.annotation_creator.add_categories(categories_df)

    def add_sounds(self):
        wav_files = []
        for root, _, files in os.walk(self.sound_files_path):
            for file in files:
                if file.endswith(".wav"):
                    wav_files.append(os.path.join(root, file))
        
        for i, file_path in enumerate(wav_files):
            duration, sample_rate = self.annotation_creator._get_duration_and_sample_rate(file_path)
            rel_path = os.path.relpath(file_path, self.data_path)
            
            self.annotation_creator.add_sound(
                id=i,
                file_name_path=rel_path,
                duration=duration,
                sample_rate=sample_rate,
                latitude=None,
                longitude=None,
                date_recorded=None
            )

    def add_annotations(self):
        annotation_files = []
        for root, _, files in os.walk(self.annotation_files_path):
            for file in files:
                if file.endswith(".txt"):
                    annotation_files.append(os.path.join(root, file))
        
        for file_path in annotation_files:
            with open(file_path, mode='r') as file:
                lines = file.readlines()
                header = [h.strip() for h in lines[0].split('\t')]
                
                if not {'Begin Time (s)', 'End Time (s)', 'Low Freq (Hz)', 'High Freq (Hz)', 'Species'}.issubset(set(header)):
                    continue
                
                reader = csv.DictReader(lines[1:], delimiter='\t', fieldnames=header)
                for i, row in enumerate(reader):
                    filename = os.path.basename(file_path).replace(".Table.1.selections.txt", ".wav")
                    sound_id = next((s["id"] for s in self.annotation_creator.data["sounds"] if filename in s["file_name_path"]), None)
                    if sound_id is None:
                        continue
                    
                    category = row['Species']
                    category_id = next((cat["id"] for cat in self.annotation_creator.data["categories"] if cat["name"] == category), None)
                    t_min, t_max = float(row['Begin Time (s)']), float(row['End Time (s)'])
                    f_min, f_max = float(row['Low Freq (Hz)']), float(row['High Freq (Hz)'])
                    
                    self.annotation_creator.add_annotation(
                        anno_id=i,
                        sound_id=sound_id,
                        category_id=None,
                        category=category,
                        t_min=t_min,
                        t_max=t_max,
                        f_min=f_min,
                        f_max=f_max
                    )

if __name__ == "__main__":
    dataset_path = os.path.join("..", "data", "Enabirds")
    reader = EnabirdsReader(dataset_path)
    reader.process_dataset()
