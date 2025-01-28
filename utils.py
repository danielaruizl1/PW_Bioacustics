import pandas as pd
import os

def split_csv_by_filename(input_csv_path):  

    df = pd.read_csv(input_csv_path)   
    absolute_path = os.path.abspath(input_csv_path)  
    directory_path = os.path.dirname(absolute_path)  
    output_dir = os.path.join(directory_path, 'annotations')  
    
    if os.path.exists(output_dir):
        return output_dir
    else:
        os.makedirs(output_dir)
      
    grouped = df.groupby('Filename')  
      
    for filename, group in grouped:   
        output_csv_path = os.path.join(output_dir, f"{filename}.csv")  
        group.to_csv(output_csv_path, index=False)

    return output_dir