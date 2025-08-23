from pydantic import BaseModel
from typing import Optional
from enum import Enum

class SequencingType(str, Enum):
    SINGLE_END = "single-end"
    PAIRED_END = "paired-end"

class AnalysisBase(BaseModel):
    classifier: str = "naive-bayes"
    reference_sequences: str = "silva"
    reference_db: str = "gtdb"
    minlen: int = 150
    maxns: int = 5
    maxee: float = 2.0
    additional_email: Optional[str] = None
    analysis_name: Optional[str] = None

class IlluminaAnalysis(AnalysisBase):
    sequencing_type: SequencingType = SequencingType.SINGLE_END
    adapter: str = "default"
    min_quality: int = 20
    max_ambiguous: int = 2

class NanoporeAnalysis(AnalysisBase):
    trim_first_bases: int = 80
    trim_after_base: int = 700
    min_quality: Optional[int] = None
    max_ambiguous: Optional[int] = None

class AnalysisResponse(BaseModel):
    job_id: str
    status: str
    message: str