import os
import csv
import argparse
import requests
import pandas as pd
from coco_standard_format import AnnotationCreator

# Define available datasets
DATASETS = [
    "Beehive", "Chiffchaff_LittleOwl_TreePipit", "CLO-43SD", "Colombia_Costa_Rica_Birds", "DV3V", 
    "Domestic_Canari", "Enabirds", "ff1010bird", "HumBugDB", "North_American_Bird_Species", 
    "Southwestern_Amazon_Basin_Soundscape", "warblrb10k"
]

class BaseReader:
    def __init__(self, data_path):
        self.data_path = data_path
        self.output_path = os.path.join(data_path, "annotations.json")
        self.annotation_creator = AnnotationCreator()
    
    def add_dataset_info(self):
        """Method to add dataset metadata (to be implemented in subclasses)."""
        raise NotImplementedError("This method should be implemented in a subclass.")
    
    def add_sounds(self):
        """Method to add sounds (to be implemented in subclasses)."""
        raise NotImplementedError("This method should be implemented in a subclass.")

    def add_categories(self):
        """Method to add categories (to be implemented in subclasses)."""
        raise NotImplementedError("This method should be implemented in a subclass.")
    
    def add_annotations(self):
        """Method to add annotations (to be implemented in subclasses)."""
        raise NotImplementedError("This method should be implemented in a subclass.")

    def save_dataset(self):
        """Saves the processed dataset as a JSON file."""
        self.annotation_creator.save_to_file(self.output_path)

    def process_dataset(self):
        """Executes the full dataset processing pipeline."""
        self.add_dataset_info()
        self.add_sounds()
        self.add_categories()
        self.add_annotations()
        self.save_dataset()

class ColombiaCostaRicaBirdsReader(BaseReader):
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

            self.annotation_creator.add_sound(i, file_name, duration, sample_rate, latitude, longitude, date_recorded)

    def add_categories(self):
        categories_df = pd.read_csv(self.species_file)
        # Ensure "Name" column exists; if not, use the first column
        if "Name" not in categories_df.columns:
            categories_df.rename(columns={categories_df.columns[0]: "Name"}, inplace=True)
        self.annotation_creator.add_categories(categories_df)

    def add_annotations(self):
        with open(self.annotation_file, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                filename, t_min, t_max, f_min, f_max, category = row['Filename'], float(row['Start Time (s)']), float(row['End Time (s)']), float(row['Low Freq (Hz)']), float(row['High Freq (Hz)']), row['Species eBird Code']

                sound_id = next((s["id"] for s in self.annotation_creator.data["sounds"] if s["file_name"] == filename), None)
                if sound_id is None:
                    continue

                category_match = [cat for cat in self.annotation_creator.data["categories"] if cat["Name"] == category]
                if not category_match:
                    continue
                category_id = category_match[0]["id"]

                anno_id = csv_reader.line_num - 2
                self.annotation_creator.add_annotation(anno_id=anno_id, sound_id=sound_id, category_id=category_id, category=category, t_min=t_min, t_max=t_max, f_min=f_min, f_max=f_max)

class SouthwesternAmazonBasinSoundscape(BaseReader):
    def __init__(self, data_path):
        super().__init__(data_path)
        self.sound_files_path = os.path.join(self.data_path, "soundscape_data")
        self.annotation_file = os.path.join(self.data_path, "annotations.csv")
        self.species_file = os.path.join(self.data_path, "species.csv")

    def add_dataset_info(self):
        self.annotation_creator.add_info(url="https://zenodo.org/records/7079124")

    def add_sounds(self):
        flac_files = [f for f in os.listdir(self.sound_files_path) if f.endswith('.flac')]
        for i, file_name in enumerate(flac_files):
            file_path = os.path.join(self.sound_files_path, file_name)
            duration, sample_rate = self.annotation_creator._get_duration_and_sample_rate(file_path)

            latitude, longitude = (5.59, -75.85) if "S01" in file_name else (10.11, -84.52) if "S02" in file_name else (None, None)
            date_recorded = file_name.split('_')[3]

            self.annotation_creator.add_sound(i, file_name, duration, sample_rate, latitude, longitude, date_recorded)

    def add_categories(self):
        categories_df = pd.read_csv(self.species_file)
        # Ensure "Name" column exists; if not, use the first column
        if "Name" not in categories_df.columns:
            categories_df.rename(columns={categories_df.columns[0]: "Name"}, inplace=True)
        self.annotation_creator.add_categories(categories_df)

    def add_annotations(self):
        with open(self.annotation_file, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                filename, t_min, t_max, f_min, f_max, category = row['Filename'], float(row['Start Time (s)']), float(row['End Time (s)']), float(row['Low Freq (Hz)']), float(row['High Freq (Hz)']), row['Species eBird Code']

                sound_id = next((s["id"] for s in self.annotation_creator.data["sounds"] if s["file_name"] == filename), None)
                if sound_id is None:
                    continue

                category_match = [cat for cat in self.annotation_creator.data["categories"] if cat["Name"] == category]
                if not category_match:
                    continue
                category_id = category_match[0]["id"]

                anno_id = csv_reader.line_num - 2
                self.annotation_creator.add_annotation(anno_id=anno_id, sound_id=sound_id, category_id=category_id, category=category, t_min=t_min, t_max=t_max, f_min=f_min, f_max=f_max)

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
                self.annotation_creator.add_sound(
                    id=sound_id,
                    file_name=file,
                    duration=duration,
                    sample_rate=sample_rate,
                    latitude=None,
                    longitude=None
                )
    
    def add_categories(self):
        """Extracts unique categories from all annotation files."""
        unique_labels = set()
        for file_list in self.annotation_files.values():
            for annotation_file in file_list:
                df = pd.read_csv(annotation_file, sep='\t', header=None, names=["start_time", "end_time", "label"])
                unique_labels.update(df["label"].dropna().unique())
        categories_df = pd.DataFrame(sorted(unique_labels), columns=['label'])
        self.annotation_creator.add_categories(categories_df)
    
    def add_annotations(self):
        """Parses the Audacity annotation files and adds the annotations."""
        for sound_file, file_list in self.annotation_files.items():
            sound_entry = next((s for s in self.annotation_creator.data["sounds"] if s["file_name"].startswith(sound_file)), None)
            if sound_entry is None:
                continue
            sound_id = sound_entry["id"]
            
            for annotation_file in file_list:
                df = pd.read_csv(annotation_file, sep='\t', header=None, names=["start_time", "end_time", "label"])
                df.dropna(inplace=True)
                for _, row in df.iterrows():
                    category_id = next(
                        (cat["id"] for cat in self.annotation_creator.data["categories"] if cat["label"] == row["label"]), None
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

class DatasetFactory:
    @staticmethod
    def get_reader(dataset_name, data_path):
        if dataset_name == "Colombia_Costa_Rica_Birds":
            return ColombiaCostaRicaBirdsReader(data_path)
        elif dataset_name == "Southwestern_Amazon_Basin_Soundscape":
            return SouthwesternAmazonBasinSoundscape(data_path)
        elif dataset_name == "Domestic_Canari":
            return DomesticCanari(data_path)
        else:
            raise ValueError(f"No reader implemented for dataset: {dataset_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process bioacoustics datasets.")
    parser.add_argument("--dataset", type=str, choices=DATASETS, required=True, help="Name of the dataset to process.")
    parser.add_argument("--data_path", type=str, default="./data", help="Path to the dataset directory.")
    args = parser.parse_args()

    # Construct full dataset path
    dataset_path = os.path.join(args.data_path, args.dataset)

    # Get the corresponding dataset reader
    reader = DatasetFactory.get_reader(args.dataset, dataset_path)

    # Process dataset
    reader.process_dataset()

