import pandas as pd  
import crowsetta
import pathlib
import os

def load_csv_annotations(file_path):  
    """  
    Load a CSV file with annotations and convert it to a Pandas DataFrame.  
  
    Parameters:  
    file_path (str): The path to the CSV file.  
  
    Returns:  
    DataFrame: A DataFrame containing the data from the CSV file.  
    """        
    dataframe = pd.read_csv(file_path)  
    return dataframe  

def get_annotations(annotations_path, format, annot_col=None):

    paths = sorted(pathlib.Path(annotations_path).glob('*.txt'))
    scribe = crowsetta.Transcriber(format=format)

    annots = []
    for path in paths:
        if annot_col != None:
            annots.append(scribe.from_file(path, annot_col=annot_col).to_annot())
        else:
            annots.append(scribe.from_file(path).to_annot())
    
    return annots

# Example with Enabirds dataset
raven_annotations_path = os.path.join(".","data","Enabirds","annotation_Files","Recording_2")
raven_annotations = get_annotations(raven_annotations_path, "raven", "Species")
print(raven_annotations[0])

# Example with Domestic Canari dataset
audacity_annotations_path = os.path.join(".","data","Domestic_Canari","M1-2016-spring_audacity_annotations","audacity-annotations")
audacity_annotations = get_annotations(audacity_annotations_path, "aud-seq")
print(audacity_annotations[0])