# PW_Bioacustics

The lack of standardized annotation formats in bioacoustics has made collaboration between research teams and data integration challenging, limiting the potential for large-scale studies and the development of effective machine learning models. We aim to establish a unified format for annotating biacoustic data, inspired by the widely used COCO format in computer vision. 

## Standardized format

The proposed JSON format contains the following sections:

```json
{
    "info": {
        "year": 2025,
        "version": 1.0,
        "description": "This is a brief summary of the dataset",
        "contributor": "Organization Name",
        "url": "https://example.com",
        "date_created": "20250101",
        "license": "CC BY 4.0"
    },
    "categories": [
        {
            "id": 0,
            "name": "Melanerpes formicivorus",
        }
    ],
    "sounds": [
        {
            "id": 0,
            "file_name": "recording1.wav",
            "duration": 120.5,
            "sample_rate": 48000,
            "latitude": 10.11,
            "longitude": -84.52,
            "date_recorded": "20230915"
        }
    ],
    "annotations": [
        {
            "anno_id": 0,
            "sound_id": 0,
            "category_id": 0,
            "category": "Melanerpes formicivorus",
            "supercategory": "animal",
            "t_min": 0.0,
            "t_max": 10.0,
            "f_min": 300.0,
            "f_max": 8000.0,
            "ischorus": false
        }
    ]
}  
```
As evidenced in the example above, our format consists of four main parts: 
- `info`: General information about the dataset
- `categories`: List of categories in the dataset
- `sounds`: List of sound files in the dataset
- `annotations`: List of annotations for the sound files 
  
Now, let's take a detailed look at the information that comprises these sections.

## Info
  
| Name           | Definition                                                                                     | Type   |  
|----------------|------------------------------------------------------------------------------------------------|--------|  
| `year` | The year when the dataset was released. <br><br> **Constraints** <br>• required: `false` | `int` |  
| `version`      | The version number of the dataset. <br><br> **Constraints** <br>• required: `false` | `float`      |  
| `description`  | A brief summary of the dataset. <br><br> **Constraints** <br>• required: `false` | `str`      |  
| `contributor`  | The name of the individual or organization that contributed the data. <br><br> **Constraints** <br>• required: `false` | `str`      |  
| `url`          | The web address where the dataset can be accessed or downloaded. <br><br> **Constraints** <br>• required: `false` | `str`      |  
| `date_created` | The datetime when the bioacoustic dataset was created in YYYYMMDD format. <br><br> **Constraints** <br>• required: `false` | `datetime` | 
| `license`         | The name of the license that specifies the permissions and restrictions for using the bioacoustic dataset. <br><br> **Constraints** <br>• required: `true` <br><br> **Example:** `CC BY 4.0` <br><br> | `str`      |  

## Categories 
  
| Name           | Definition                                                                                     | Type   |  
|----------------|------------------------------------------------------------------------------------------------|--------|
| `id`           | A unique identifier for a category within the dataset. <br><br> **Constraints** <br>• required: `true` <br><br> **Example:** `0`| `int`      |
| `name`    | The name of the category of sounds, such as a particular species or type of call. <br><br> **Constraints** <br>• required: `true` <br><br> **Example:** `Melanerpes formicivorus` | `str`      |  

This section is built from a DataFrame that must include at least the category names and their identifiers. However, it can also contain other relevant category information, such as eBird Codes, Common Names, etc.

## Sounds 
  
| Name           | Definition                                                                                     | Type   |  
|----------------|------------------------------------------------------------------------------------------------|--------|  
| `id`           | A unique identifier for a specific sound within the dataset. <br><br> **Constraints** <br>• required: `true` <br><br> **Example:** `1`| `int`      |  
| `file_name`    | The name of the audio file containing the bioacoustic recording. <br><br> **Constraints** <br>• required: `true` <br><br> **Example:** `recording1.wav` | `str`      |  
| `duration`     | The length of the audio recording in seconds. <br><br> **Constraints** <br>• required: `true` <br><br> **Example:** `120.5`| `float`      |  
| `sample_rate`  | The number of samples of audio carried per second, measured in Hz. <br><br> **Constraints** <br>• required: `true` <br><br> **Example:** `48000`| `int`      |  
| `latitude`     | The geographical latitude where the bioacoustic recording was taken. <br><br> **Constraints** <br>• required: `true` <br><br> **Example:** `10.11` | `float`    |  
| `longitude`    | The geographical longitude where the bioacoustic recording was taken. <br><br> **Constraints** <br>• required: `true` <br><br> **Example:** `-84.52` | `float`    |  
| `date_recorded`| The datetime when the audio was recoded in YYYYMMDD format. <br><br> **Constraints** <br>• required: `false` | `datetime`    |  


## Annotations 
  
| Name           | Definition                                                                                     | Type   |  
|----------------|------------------------------------------------------------------------------------------------|--------|  
| `anno_id`           | A unique identifier for a specific annotation within the dataset. <br><br> **Constraints** <br>• required: `true` <br><br> **Example:** `1` | `int`      |  
| `sound_id`     | The identifier of the sound to which the annotation is linked. <br><br> **Constraints** <br>• required: `true` <br><br> **Example:** `1` | `int`      |  
| `category_id`  | The identifier of the category to which the sound belongs. <br><br> **Constraints** <br>• required: `true` <br><br> **Example:** `0` | `int`      | 
| `category`  | The name of the category of sounds, such as a particular species or type of call. <br><br> **Constraints** <br>• required: `true` <br><br> **Example:** `"Melanerpes formicivorus"` | `int`      | 
| `supercategory`| A higher-level grouping that the category belongs to. <br><br> **Constraints** <br>• required: `false` | `str`      |   
| `t_min`        | The starting time of the annotated sound within the recording, in seconds. <br><br> **Constraints** <br>• required: `true` <br><br> **Example:** `0.0` | `float`    |  
| `t_max`        | The ending time of the annotated sound within the recording, in seconds. <br><br> **Constraints** <br>• required: `true` <br><br> **Example:** `10.0` | `float`    |  
| `f_min`        | The lowest frequency of the annotated sound within the recording, in Hz. <br><br> **Constraints** <br>• required: `false`| `float`    |  
| `f_max`        | The highest frequency of the annotated sound within the recording, in Hz. <br><br> **Constraints** <br>• required: `false` | `float`    |  
| `ischorus`     | A boolean indicating whether the sound is a chorus or not. <br><br> **Constraints** <br>• required: `true` <br><br> **Example:** `false` <br><br> | `bool`     |  
