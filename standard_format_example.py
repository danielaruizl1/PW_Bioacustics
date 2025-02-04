#%%
from coco_standard_format import AnnotationCreator
from datetime import datetime
import pandas as pd
import csv
import os

# Create an instance of AnnotationCreator 
annotation_creator = AnnotationCreator()

#%% Add the dataset information
annotation_creator.add_info(year = 2019, 
                version = 1.0, 
                description = "This collection contains 34 hour-long soundscape recordings, which have been annotated by expert ornithologists who provided 6,952 bounding box labels for 89 different bird species from Colombia and Costa Rica. The data were recorded in 2019 at two highly diverse neotropical coffee farm landscapes from the towns of Jardín, Colombia and San Ramon, Costa Rica. This collection has partially been featured as test data in the 2021 BirdCLEF competition and can primarily be used for training and evaluation of machine learning algorithms.", 
                contributor = "Álvaro Vega-Hidalgo, Stefan Kahl, Laurel B. Symes, Viviana Ruiz-Gutiérrez, Ingrid Molina-Mora, Fernando Cediel, Luis Sandoval, & Holger Klinck", 
                url="https://zenodo.org/records/7525349", 
                date_created="20230111",
                license="CC BY 4.0",
                )

#%% Add the sound entries to the dataset
sound_files_path = os.path.join(".","data","Colombia_Costa_Rica_Birds","soundscape_data") 
flac_files = [f for f in os.listdir(sound_files_path) if f.endswith('.flac')]  
   
for i, file_name in enumerate(flac_files):   
    file_path = os.path.join(sound_files_path, file_name)   
    duration, sample_rate = annotation_creator._get_duration_and_sample_rate(file_path)
    
    if "S01" in file_name:
        latitude = 5.59   
        longitude = -75.85
    elif "S02" in file_name:
        latitude = 10.11
        longitude = -84.52   

    date_recorded = file_name.split('_')[3]  
  
    annotation_creator.add_sound(i, file_name, duration, sample_rate, latitude, longitude, date_recorded) 

#%% Add the categories to the dataset
categories_df = pd.read_csv(os.path.join(".","data","Colombia_Costa_Rica_Birds","species.csv"))
annotation_creator.add_categories(categories_df)

#%% Add the annotations to the dataset
annotation_file = os.path.join(".","data","Colombia_Costa_Rica_Birds","annotations.csv") 

with open(annotation_file, mode='r') as file:  
    csv_reader = csv.DictReader(file)  
    for row in csv_reader:  
        filename = row['Filename']  
        t_min = float(row['Start Time (s)'])  
        t_max = float(row['End Time (s)'])  
        f_min = float(row['Low Freq (Hz)'])  
        f_max = float(row['High Freq (Hz)'])  
        category = row['Species eBird Code']  
  
        for sound in annotation_creator.data["sounds"]:
            if sound["file_name"] == filename:
                sound_id = sound["id"]
                break

        category_id = [cat for cat in annotation_creator.data["categories"] if cat["Species eBird Code"] == category][0]["id"]
        anno_id = csv_reader.line_num - 2  
  
        annotation_creator.add_annotation(anno_id, sound_id, category_id, category, t_min, t_max, f_min=f_min, f_max=f_max)  

#%% Save the dataset to a JSON file
annotation_creator.save_to_file(os.path.join(".","data","Colombia_Costa_Rica_Birds","coco_annotations.json"))
