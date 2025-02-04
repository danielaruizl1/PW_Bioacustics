import pandas as pd  
import numpy as np
import crowsetta
import pathlib
import attr
import os

from typing import ClassVar
from crowsetta.typing import PathLike
from utils import split_csv_by_filename

@crowsetta.formats.register_format
@crowsetta.interface.BBoxLike.register
@attr.define
class csv_bbox:
    """Example custom annotation format for Colombia_Costa_Rica_Birds dataset"""
    name: ClassVar[str] = 'csv_bbox'
    ext: ClassVar[str] = '.csv'

    df: pd.DataFrame 
    annot_path: pathlib.Path = attr.field(converter=pathlib.Path)
    audio_path: np.ndarray = attr.field(eq=attr.cmp_using(eq=np.array_equal))  
    
    @classmethod
    def from_file(cls, annot_path: PathLike):
        
        annot_path = pathlib.Path(annot_path)  
        crowsetta.validation.validate_ext(annot_path, extension=cls.ext)  
  
        df = pd.read_csv(annot_path)  
          
        audio_paths = df['Filename'].values[0]  
        
        return cls(df = df,
            annot_path = annot_path,
            audio_path = audio_paths)

    def to_bbox(self):
        bboxes = []
        for begin_time, end_time, low_freq, high_freq, Species in zip(
            self.df['Start Time (s)'].values,
            self.df['End Time (s)'].values,
            self.df['Low Freq (Hz)'].values,
            self.df['High Freq (Hz)'].values,
            self.df['Species eBird Code'].values,
        ):
            bboxes.append(
                crowsetta.BBox(onset=begin_time, offset=end_time, low_freq=low_freq, high_freq=high_freq, label=Species)
            )
        return bboxes
    
    def to_annot(self):
        bboxes = self.to_bbox()
        return crowsetta.Annotation(annot_path=self.annot_path, notated_path=self.audio_path, bboxes=bboxes)


def get_annotations(annotations_path, format, annot_col=None, annot_ext="txt"):

    paths = sorted(pathlib.Path(annotations_path).glob(f'*.{annot_ext}'))
    scribe = crowsetta.Transcriber(format=format)
    annots = []
    for path in paths:
        if annot_col != None:
            annots.append(scribe.from_file(path, annot_col=annot_col).to_annot())
        else:
            annots.append(scribe.from_file(path).to_annot())
    
    return annots

if __name__ == "__main__":
    
    # Example with Colombia_Costa_Rica_Birds
    custom_annotations_path = split_csv_by_filename(os.path.join(".","data","Colombia_Costa_Rica_Birds","annotations.csv"))
    custom_annotations = get_annotations(custom_annotations_path, "csv_bbox", annot_ext="csv")
    print(custom_annotations[0])

    # Example with Enabirds dataset
    raven_annotations_path = os.path.join(".","data","Enabirds","annotation_Files","Recording_2")
    raven_annotations = get_annotations(raven_annotations_path, "raven", annot_col="Species")
    print(raven_annotations[0])

    # Example with Domestic Canari dataset
    audacity_annotations_path = os.path.join(".","data","Domestic_Canari","M1-2016-spring_audacity_annotations","audacity-annotations")
    audacity_annotations = get_annotations(audacity_annotations_path, "aud-seq")
    print(audacity_annotations[0])