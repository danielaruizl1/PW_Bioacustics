from datetime import datetime  
from typing import Optional
import soundfile as sf 
import pandas as pd
import json  
import os
  
class AnnotationCreator:  
    """  
    A class to create and manage bioacustics annotations in a standard format.  
  
    Attributes:  
        data (dict): A dictionary to store general info, sounds, and annotations of a bioacustics dataset.  
    """  
  
    def __init__(self):  
        """  
        Initializes the AnnotationCreator with an empty dataset.  
        """
        self.data = {  
            "info": {},
            "categories": [],  
            "sounds": [],  
            "annotations": []  
        }  

    def _validate_date_format(self, date_str: str, date_format: str = "%Y%m%d"):  
        """  
        Validates if the date string matches the given format and is not a future date.  
  
        Args:  
            date_str (str): The date string to validate.  
            date_format (str): The expected format of the date string.  
  
        Raises:  
            ValueError: If the date string does not match the format or is a future date.  
        """  
        try:  
            date_obj = datetime.strptime(date_str, date_format)  
        except ValueError:  
            raise ValueError(f"Date '{date_str}' is not in the correct format. Expected format: {date_format}")  

        if date_obj > datetime.now():  
            raise ValueError("Future dates are invalid.")
    
    def _get_duration_and_sample_rate(self, file_path:str):   
        """
        Get the duration and sample rate of a sound file

        Args:
            file_path (str): The path to the sound file

        Returns:
            duration (float): The duration of the sound file in seconds
            sample_rate (int): The sample rate of the sound file in Hz
        """
        with sf.SoundFile(file_path) as sound_file:  
            duration = len(sound_file) / sound_file.samplerate  
            sample_rate = sound_file.samplerate 
        return duration, sample_rate

    def add_info(self, license:str, year:Optional[int]=None, version:Optional[float]=None, description:Optional[str]=None, contributor:Optional[str]=None, url:Optional[str]=None, date_created:Optional[datetime]=None):
        """  
        Adds the general information about the dataset.  
  
        Args:  
            license (str): The name of the license that specifies the permissions and restrictions for using the bioacoustic dataset.  
            year (Optional[int]): The year when the dataset was released.  
            version (Optional[float]): The version number of the dataset.  
            description (Optional[str]): A brief summary of the dataset.  
            contributor (Optional[str]): The name of the individual or organization that contributed the data.  
            url (Optional[str]): The web address where the dataset can be accessed or downloaded.  
            date_created (Optional[str]): The datetime when the bioacoustic dataset was created in YYYY-MM-DD format.  
  
        Raises:  
            ValueError: If the year is in the future or the date format is incorrect.  
        """  
        if year > int(datetime.now().year):  
            raise ValueError("Year must be the current or a previous one.") 
        if date_created:
            self._validate_date_format(date_created)

        self.data["info"]["year"] = year
        self.data["info"]["version"] = version
        self.data["info"]["description"] = description
        self.data["info"]["contributor"] = contributor
        self.data["info"]["url"] = url
        self.data["info"]["date_created"] = date_created
        self.data["info"]["license"] = license  
    
    def add_categories(self, categories_df:pd.DataFrame):
        """  
        Adds the categories ids and names to the dataset.  
  
        Args:  
            categories (DataFrame): A pandas DataFrame containing the category information.  
        """  
        sorted_df = categories_df.sort_values(by=categories_df.columns[0]) 
        sorted_df.reset_index(drop=True, inplace=True)  
        sorted_df.index.name = 'id'
        categories_list = sorted_df.reset_index().to_dict(orient='records') 
        self.data['categories'] = categories_list
        
    def add_sound(self, id:int, file_name:str, duration:int, sample_rate:int, latitude:float, longitude:float, date_recorded:Optional[datetime]=None):  
        """  
        Adds a sound entry to the dataset.  
  
        Args:  
            id (int): A unique identifier for a specific sound within the dataset.  
            file_name (str): The name of the audio file containing the bioacoustic recording.  
            duration (float): The length of the audio recording in seconds.  
            sample_rate (int): The number of samples of audio carried per second, measured in Hz.  
            latitude (float): The geographical latitude where the bioacoustic recording was taken.  
            longitude (float):The geographical longitude where the bioacoustic recording was taken.  
            date_recorded (Optional[str]): The datetime when the audio was recoded in YYYY-MM-DD format.  
  
        Raises:  
            ValueError: If duration, sample rate, latitude, or longitude are out of valid range,  
                        or if the date format is incorrect.  
        """
        if duration <= 0:  
            raise ValueError("Duration must be a positive value.")  
        if sample_rate <= 0:  
            raise ValueError("Sample rate must be a positive value.")
        if latitude:
            if not (-90 <= latitude <= 90):  
                raise ValueError("Latitude must be between -90 and 90 degrees.")  
        if longitude:
            if not (-180 <= longitude <= 180):  
                raise ValueError("Longitude must be between -180 and 180 degrees.")
        if date_recorded:
            self._validate_date_format(date_recorded)

        sound = {  
            "id": id,  
            "file_name": file_name,  
            "duration": duration,  
            "sample_rate": sample_rate,  
            "latitude": latitude,  
            "longitude": longitude,  
            "date_recorded": date_recorded  
        }  
        self.data['sounds'].append(sound)  
  
    def add_annotation(self, anno_id:int, sound_id:int, category_id:int, category:str, t_min:float, t_max:float, supercategory:Optional[str]=None, f_min:Optional[float]=None, f_max:Optional[float]=None, ischorus:Optional[bool]=None):  
        """  
        Adds an annotation entry to the dataset.  
    
        Args:  
            anno_id (int):  A unique identifier for a specific annotation within the dataset.  
            sound_id (int): The identifier of the sound to which the annotation is linked.  
            category_id (int): The identifier of the category to which the sound belongs.  
            category (str): The name of the category of sounds, such as a particular species or type of call.  
            t_min (float): The starting time of the annotated sound within the recording, in seconds.  
            t_max (float): The ending time of the annotated sound within the recording, in seconds.  
            supercategory (Optional[str]): A higher-level grouping that the category belongs to.  
            f_min (Optional[float]): The lowest frequency of the annotated sound within the recording, in Hz.  
            f_max (Optional[float]): The highest frequency of the annotated sound within the recording, in Hz  
            ischorus (Optional[bool]): A boolean indicating whether the sound is a chorus or not.  
    
        Raises:  
            ValueError: If any of the provided values are out of valid range, or if the   
                        time/frequency constraints are violated.  
        """
        sound_dict = self.data['sounds'][sound_id]
        
        if t_min < 0:  
            raise ValueError("t_min must be a positive value.")  
        if t_max < 0:  
            raise ValueError("t_max must be a positive value.")
        if t_max < t_min:
            raise ValueError("t_max must be greater than t_min.")
        if t_max > round(sound_dict["duration"],1):
            raise ValueError("t_max must be less than the duration of the sound.")
        if f_min and f_max:
            if f_min < 0:
                raise ValueError("f_min must be a positive value.")
            if f_max < 0:
                raise ValueError("f_max must be a positive value.")
            if f_max < f_min:
                raise ValueError("f_max must be greater than f_min.")
            if f_max > sound_dict["sample_rate"] / 2:
                raise ValueError("f_max must be less than half the sample rate of the sound.")

        annotation = {  
            "anno_id": anno_id,  
            "sound_id": sound_id,  
            "category_id": category_id,  
            "category": category,  
            "supercategory": supercategory,  
            "t_min": t_min,  
            "t_max": t_max,  
            "f_min": f_min,  
            "f_max": f_max,  
            "ischorus": ischorus  
        }  
        self.data['annotations'].append(annotation)  

    def convert_crowsetta_bbox_annotations(self, crowsetta_annotations:list):
        """  
        Adds annotations from Crowsetta to the dataset.  
  
        Args:  
            crowsetta_annotations (list): A list of annotations in Crowsetta format.
        """
        # Add categories 
        unique_labels = set()   
        for annot in crowsetta_annotations:  
            for bbox in annot.bboxes:  
                unique_labels.add(bbox.label) 

        categories_df = pd.DataFrame(list(unique_labels), columns=['label'])
        self.add_categories(categories_df)

        # Add sounds 
        for sound_id, annotation in enumerate(crowsetta_annotations):
            duration, sample_rate = self._get_duration_and_sample_rate(annotation.notated_path)
            self.add_sound(id=sound_id, 
                           file_name=annotation.notated_path.name, 
                           duration=duration, 
                           sample_rate=sample_rate,
                           latitude=None,
                           longitude=None)
            # Add annotations
            for anno_id, bbox in enumerate(annotation.bboxes):
                category_id = [category for category in self.data["categories"] if category["label"] == bbox.label][0]["id"]
                self.add_annotation(anno_id=anno_id, 
                                    sound_id=sound_id, 
                                    category_id=category_id, 
                                    category=bbox.label, 
                                    t_min=float(bbox.onset), 
                                    t_max=float(bbox.offset), 
                                    f_min=float(bbox.low_freq), 
                                    f_max=float(bbox.high_freq))

    def convert_crowsetta_seq_annotations(self, crowsetta_annotations:list):
        """  
        Adds annotations from Crowsetta to the dataset.  
  
        Args:  
            crowsetta_annotations (list): A list of annotations in Crowsetta format.
        """
        # Add categories 
        unique_labels = set()   
        for annot in crowsetta_annotations:  
            for segment in annot.seq.segments:  
                unique_labels.add(segment.label) 

        categories_df = pd.DataFrame(list(unique_labels), columns=['label'])
        self.add_categories(categories_df)

        # Add sounds 
        for sound_id, annotation in enumerate(crowsetta_annotations):
            duration, sample_rate = self._get_duration_and_sample_rate(annotation.notated_path)
            self.add_sound(id=sound_id, 
                           file_name=annotation.notated_path.name, 
                           duration=duration, 
                           sample_rate=sample_rate,
                           latitude=None,
                           longitude=None)
            # Add annotations
            for anno_id, segment in enumerate(annotation.seq.segments):
                category_id = [category for category in self.data["categories"] if category["label"] == segment.label][0]["id"]
                self.add_annotation(anno_id=anno_id, 
                                    sound_id=sound_id, 
                                    category_id=category_id, 
                                    category=segment.label, 
                                    t_min=float(segment.onset_s), 
                                    t_max=float(segment.offset_s))
  
    def save_to_file(self, filename):  
        """  
        Saves the current dataset to a JSON file.  
    
        Args:  
            filename (str): The name of the file to save the dataset to.  
        """
        with open(filename, 'w') as f:  
            json.dump(self.data, f, indent=4)  

if __name__ == "__main__":

    # Example of how to use the AnnotationCreator class and its methods
    creator = AnnotationCreator()  

    creator.add_info(year=2025, 
                    version=1.0, 
                    description="This is a brief summary of the dataset", 
                    contributor="Organization Name", 
                    url="https://example.com", 
                    date_created="20250101",
                    license="CC BY 4.0",)
    
    creator.add_categories(pd.DataFrame([{'name': 'Melanerpes formicivorus'}]))

    creator.add_sound(id=0, 
                    file_name="recording1.wav",
                    duration=120.5,
                    sample_rate=48000,
                    latitude=10.11,
                    longitude=-84.52,
                    date_recorded="20230915")

    creator.add_annotation(anno_id=0,
                        sound_id=0,
                        category_id=0,
                        category="Melanerpes formicivorus",
                        supercategory="animal",
                        t_min=0.0,
                        t_max=10.0,
                        f_min=300.0,
                        f_max=8000.0,
                        ischorus=False)

    creator.save_to_file("annotations.json")  