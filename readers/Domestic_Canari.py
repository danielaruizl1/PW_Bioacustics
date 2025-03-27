from BaseReader import BaseReader
import pandas as pd
import requests
import csv
import os

class DomesticCanari(BaseReader):
    def __init__(self, data_path):
        super().__init__(data_path)
        self.sound_files_path = os.path.join(self.data_path, "M1-2016-sping_audio", "audio")
        self.annotation_files_path = os.path.join(self.data_path, "M1-2016-spring_audacity_annotations", "audacity-annotations")
        self.annotation_files = self._find_annotation_files()
    
    def _find_annotation_files(self):
        """Finds all Audacity annotation files in the dataset directory."""
        annotation_files = {}
        for file in os.listdir(self.annotation_files_path):
            if file.endswith(".txt"):
                base_name = os.path.splitext(file)[0]
                if base_name not in annotation_files:
                    annotation_files[base_name] = []
                annotation_files[base_name].append(os.path.join(self.annotation_files_path, file))
        if not annotation_files:
            raise FileNotFoundError("No Audacity annotation files found in the dataset directory.")
        return annotation_files
    
    def add_dataset_info(self):
        """Adds metadata about the dataset."""
        self.annotation_creator.add_info(url="https://zenodo.org/records/6521932")
    
    def add_sounds(self):
        """Extracts sound file information from the dataset directory."""
        for file in os.listdir(self.sound_files_path):
            if file.endswith(".wav"):
                file_path = os.path.join(self.sound_files_path, file)
                duration, sample_rate = self.annotation_creator._get_duration_and_sample_rate(file_path)
                sound_id = len(self.annotation_creator.data["sounds"])
                # TODO: Add date_recorded from filename
                self.annotation_creator.add_sound(
                    id=sound_id,
                    file_name_path= os.path.join(os.path.relpath(self.sound_files_path, self.data_path), file),
                    duration=duration,
                    sample_rate=sample_rate,
                    latitude=None,
                    longitude=None,
                    date_recorded=None
                )
    
    def add_categories(self):
        """Extracts unique categories from all annotation files."""
        unique_labels = set()
        for file_list in self.annotation_files.values():
            for annotation_file in file_list:
                df = pd.read_csv(annotation_file, sep='\t', header=None, names=["start_time", "end_time", "label"])
                unique_labels.update(df["label"].dropna().unique())
        categories_df = pd.DataFrame(sorted(unique_labels), columns=['label'])
        # Ensure "name" column exists; if not, use the first column
        if "name" not in categories_df.columns:
            categories_df.rename(columns={categories_df.columns[0]: "name"}, inplace=True)
        self.annotation_creator.add_categories(categories_df)
    
    def add_annotations(self):
        """Parses the Audacity annotation files and adds the annotations."""
        for sound_file_audacity, file_list in self.annotation_files.items():
            sound_file = sound_file_audacity.split(".")[0]
            sound_entry = next((s for s in self.annotation_creator.data["sounds"] if sound_file in s["file_name_path"]), None)
            if sound_entry is None:
                continue
            sound_id = sound_entry["id"]
            
            for annotation_file in file_list:
                df = pd.read_csv(annotation_file, sep='\t', header=None, names=["start_time", "end_time", "label"])
                df.dropna(inplace=True)
                for _, row in df.iterrows():
                    category_id = next(
                        (cat["id"] for cat in self.annotation_creator.data["categories"] if cat["name"] == row["label"]), None
                    )
                    if category_id is not None:
                        self.annotation_creator.add_annotation(
                            anno_id=len(self.annotation_creator.data["annotations"]),
                            sound_id=sound_id,
                            category_id=category_id,
                            category=row["label"],
                            t_min=row["start_time"],
                            t_max=row["end_time"]
                        )
    
    def process_dataset(self):
        """Runs the full dataset processing pipeline."""
        super().process_dataset()

if __name__ == "__main__":
    dataset_path = os.path.join("..", "data", "Domestic_Canari")
    reader = DomesticCanari(dataset_path)
    reader.process_dataset()
