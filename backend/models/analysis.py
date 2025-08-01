from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class SequencingType(str, Enum):
    SINGLE_END = "single-end"
    PAIRED_END = "paired-end"

class AnalysisBase(BaseModel):
    classifier: str = "default"
    reference_sequences: str = "default"
    reference_db: str = "default"
    minlen: Optional[int] = None
    maxns: Optional[int] = None
    maxee: Optional[float] = None
    additional_email: Optional[str] = None

class IlluminaAnalysis(AnalysisBase):
    sequencing_type: SequencingType = SequencingType.SINGLE_END
    adapter: str = "default"

class NanoporeAnalysis(AnalysisBase):
    minquality: Optional[int] = None
    max_ambig: Optional[int] = None

class AnalysisResponse(BaseModel):
    job_id: str
    status: str
    message: str