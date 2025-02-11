import pandas as pd  
import numpy as np
import crowsetta
import pathlib
import attr
import os

from typing import ClassVar
from crowsetta.typing import PathLike
from utils import split_csv_by_filename
from coco_standard_format import AnnotationCreator

@crowsetta.formats.register_format
@crowsetta.interface.BBoxLike.register
@attr.define
class csv_bbox:
    """Example custom annotation format for Colombia_Costa_Rica_Birds dataset"""
    name: ClassVar[str] = 'csv_bbox'
    ext: ClassVar[str] = '.csv'

    df: pd.DataFrame 
    annot_path: pathlib.Path = attr.field(converter=pathlib.Path)
    notated_path: np.ndarray = attr.field(eq=attr.cmp_using(eq=np.array_equal))  
    
    @classmethod
    def from_file(cls, annot_path: PathLike, notated_path: PathLike):
        annot_path = pathlib.Path(annot_path)  
        notated_path = pathlib.Path(notated_path)
        crowsetta.validation.validate_ext(annot_path, extension=cls.ext)  
        crowsetta.validation.validate_ext(notated_path, extension=".flac")
        df = pd.read_csv(annot_path)  
        return cls(df = df,
            annot_path = annot_path,
            notated_path = notated_path)

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
        return crowsetta.Annotation(annot_path=self.annot_path, notated_path=self.notated_path, bboxes=bboxes)


def get_annotations(annotations_path, format, sounds_path, annot_col=None, annot_ext="txt", sounds_ext="wav"):

    paths = sorted(pathlib.Path(annotations_path).glob(f'*.{annot_ext}'))
    sounds_paths = sorted(pathlib.Path(sounds_path).glob(f'*.{sounds_ext}'))
    assert len(paths) == len(sounds_paths), "Number of annotations and sounds must be the same"

    scribe = crowsetta.Transcriber(format=format)
    annots = []
    for i in range(len(paths)):
        if annot_col != None:
            annots.append(scribe.from_file(paths[i], annot_col=annot_col, audio_path=sounds_paths[i]).to_annot())
        else:
            annots.append(scribe.from_file(paths[i], notated_path=sounds_paths[i]).to_annot())
    
    return annots

if __name__ == "__main__":

    # Example with Domestic Canari dataset
    audacity_annotations_path = os.path.join(".","data","Domestic_Canari","M1-2016-spring_audacity_annotations","audacity-annotations")
    audacity_sounds_path = os.path.join(".","data","Domestic_Canari","M1-2016-sping_audio", "audio")
    audacity_annotations = get_annotations(audacity_annotations_path, "aud-seq", sounds_path=audacity_sounds_path)
    creator_audacity = AnnotationCreator()
    creator_audacity.convert_crowsetta_seq_annotations(audacity_annotations)
    creator_audacity.save_to_file(os.path.join(".","annotations_results","audacity_annotations_from_crowsetta.json"))

    # Example with Enabirds dataset
    raven_annotations_path = os.path.join(".","data","Enabirds","annotation_Files","Recording_3")
    raven_sounds_path = os.path.join(".","data","Enabirds","wav_Files", "Recording_3")
    raven_annotations = get_annotations(raven_annotations_path, "raven", annot_col="Species", sounds_path=raven_sounds_path)
    creator_raven = AnnotationCreator()
    creator_raven.convert_crowsetta_bbox_annotations(raven_annotations)
    creator_raven.save_to_file(os.path.join(".","annotations_results","raven_annotations_from_crowsetta.json"))

    # Example with Colombia_Costa_Rica_Birds
    custom_annotations_path = split_csv_by_filename(os.path.join(".","data","Colombia_Costa_Rica_Birds","annotations.csv"))
    custom_sounds_path = os.path.join(".","data","Colombia_Costa_Rica_Birds","soundscape_data")
    custom_annotations = get_annotations(custom_annotations_path, "csv_bbox", sounds_path=custom_sounds_path, annot_ext="csv", sounds_ext="flac")
    creator_custom = AnnotationCreator() 
    creator_custom.convert_crowsetta_bbox_annotations(custom_annotations)
    creator_custom.save_to_file(os.path.join(".","annotations_results","custom_annotations_from_crowsetta.json"))

    
    
    
    

    
