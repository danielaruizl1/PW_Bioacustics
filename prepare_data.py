from zipfile import ZipFile  
from tqdm import tqdm  
from io import BytesIO 
import argparse
import requests  
import tempfile 
import os  

def unzip_nested_files(directory):  
    for root, dirs, files in os.walk(directory):  
        for file in files:  
            if file.endswith('.zip'):  
                file_path = os.path.join(root, file)  
                folder_name = os.path.splitext(file)[0]  
                extract_path = os.path.join(root, folder_name)  
                  
                # Create the directory if it doesn't exist  
                os.makedirs(extract_path, exist_ok=True)  
                  
                with ZipFile(file_path, 'r') as zip_ref:  
                    zip_ref.extractall(extract_path)  
                  
                os.remove(file_path)  # Remove the zip file after extracting  
                print(f"Extracted nested zip file {file_path} into {extract_path}")
  
def download_and_unzip(url, extract_to='data'):  
    # Ensure the data directory exists  
    if not os.path.exists(extract_to):  
        os.makedirs(extract_to)  
      
    # Download the file from the URL  
    response = requests.get(url, stream=True)  
    if response.status_code == 200:
        
        total_size = int(response.headers.get('content-length', 0))  
        block_size = 1024  # 1 Kibibyte 

        content_disposition = response.headers.get("content-disposition")  
        filename = content_disposition.split('filename=')[1].strip('"')
        
        if filename.endswith('.zip'):

            temp_file = tempfile.NamedTemporaryFile(delete=False)  
            temp_file_path = temp_file.name  
    
            t = tqdm(total=total_size, unit='iB', unit_scale=True, desc="Downloading")  
            for data in response.iter_content(block_size):  
                t.update(len(data))  
                temp_file.write(data)  
            t.close()  
            temp_file.close()  
            if total_size != 0 and t.n != total_size:  
                print("ERROR, something went wrong")  
                return  
    
            print(f"Successfully downloaded from {url}")  

            # Unzip the file into the directory with a progress bar  
            with ZipFile(temp_file_path) as zipfile:  
                zip_info_list = zipfile.infolist()  
                for zip_info in tqdm(zip_info_list, desc="Extracting"):  
                    zipfile.extract(zip_info, extract_to)  
    
            print(f"Extracted to {extract_to}")  
    
            # Check for nested zip files and unzip them  
            unzip_nested_files(extract_to)  
    
            # Remove the temporary file  
            os.remove(temp_file_path)  

        else:
            print("The file is not a zip file")

    else:  
        print(f"Failed to download from {url}, status code: {response.status_code}")  
  
def main():

    # Dictionary of datasets, where keys are the dataset names and values are lists of URLs (some datasets may have multiple parts)
    datasets = {  
        "BirdVox-DCASE-20k": ["https://zenodo.org/api/records/1208080/files-archive"],
        "Beehive": ["https://zenodo.org/api/records/2667806/files-archive"],
        "Chiffchaff_LittleOwl_TreePipit": ["https://zenodo.org/api/records/1413495/files-archive"],
        "Colombia_Costa_Rica_Birds": ["https://zenodo.org/api/records/7525349/files-archive"],
        "Domestic_Canari": ["https://zenodo.org/api/records/6521932/files-archive"],  
        "DV3V": ["https://zenodo.org/api/records/11544734/files-archive"],
        "HumBugDB": ["https://zenodo.org/api/records/4904800/files-archive"],
        "North_American_Bird_Species": ["https://zenodo.org/api/records/1250690/files-archive"],  
        "Southwestern_Amazon_Basin_Soundscape": ["https://zenodo.org/api/records/7079124/files-archive"],
        "Pin-tailed_Whydah": ["https://zenodo.org/api/records/6330711/files-archive"], 
        "Thyolo_Alethe": ["https://zenodo.org/api/records/6328244/files-archive"],
        "Hawaii_Birds": ["https://zenodo.org/api/records/7078499/files-archive"],
        "Northeastern_US_Soundscapes": ["https://zenodo.org/api/records/7079380/files-archive"],
        "Southern_Sierra_Nevada_Birds": ["https://zenodo.org/api/records/7525805/files-archive"],
        "WABAD": ["https://zenodo.org/api/records/14191524/files-archive"],
        "Western_United_States_Soundscapes": ["https://zenodo.org/api/records/7050014/files-archive"],
    }  

    parser = argparse.ArgumentParser(description="Download and extract datasets.")
    parser.add_argument("--dataset", choices=datasets.keys(), help="Name of the dataset to download.")
    args = parser.parse_args()

    dataset_name = args.dataset
    dataset_dir = os.path.join('data', dataset_name)
    for url in datasets[dataset_name]:
        download_and_unzip(url, extract_to=dataset_dir)

if __name__ == "__main__":
    main()