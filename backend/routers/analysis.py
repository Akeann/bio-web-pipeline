from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form, status
from fastapi.responses import JSONResponse
from pathlib import Path
import uuid
import json
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from ..models.analysis import AnalysisResponse
from ..models.db_models import AnalysisJob
from ..dependencies import get_current_user
from ..models.user import UserInDB
from ..services.database import get_db

router = APIRouter(
    prefix="/api/analysis",
    tags=["Analysis"],
)

# Configuration paths
UPLOADS_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

@router.post(
    "/illumina",
    response_model=AnalysisResponse,
    summary="Illumina Analysis",
    description="Accepts FASTQ file and parameters for Illumina data analysis",
    responses={
        200: {
            "description": "Analysis started successfully",
            "content": {
                "application/json": {
                    "example": {
                        "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "status": "received",
                        "message": "Illumina data processing started"
                    }
                }
            }
        },
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        500: {"description": "File processing error"}
    }
)
async def analyze_illumina(
    fastq_file: Annotated[UploadFile, File(description="FASTQ file for analysis")],
    sequencing_type: str = Form("single-end"),
    adapter: str = Form("default"),
    min_quality: int = Form(20),
    max_ambiguous: int = Form(2),
    minlen: int = Form(150),
    maxns: int = Form(5),
    maxee: float = Form(2.0),
    classifier: str = Form("naive-bayes"),
    ref_seq: str = Form("silva"),
    ref_db: str = Form("gtdb"),
    additional_email: Optional[str] = Form(None),
    analysis_name: Optional[str] = Form(None),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process Illumina sequencing data with the following steps:
    1. Validate user authentication
    2. Save uploaded FASTQ file
    3. Create analysis job record
    4. Return job information
    """

    try:
        # Generate job ID
        job_id = str(uuid.uuid4())
        file_path = UPLOADS_DIR / f"{job_id}_{fastq_file.filename}"

        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await fastq_file.read()
            buffer.write(content)

        # Prepare parameters as JSON
        params = {
            "sequencing_type": sequencing_type,
            "adapter": adapter,
            "min_quality": min_quality,
            "max_ambiguous": max_ambiguous,
            "minlen": minlen,
            "maxns": maxns,
            "maxee": maxee,
            "classifier": classifier,
            "reference_sequences": ref_seq,
            "reference_db": ref_db,
            "additional_email": additional_email,
            "analysis_name": analysis_name
        }

        # Create database record
        db_job = AnalysisJob(
            job_id=job_id,
            # user_id=current_user.id,
            user_id=1,
            type="illumina",
            file_path=str(file_path),
            parameters=json.dumps(params),
            status="pending"
        )
        
        db.add(db_job)
        db.commit()
        db.refresh(db_job)

        return AnalysisResponse(
            job_id=job_id,
            status="received",
            message="Illumina data processing started"
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@router.post(
    "/nanopore",
    response_model=AnalysisResponse,
    summary="Nanopore Analysis",
    description="Accepts FASTQ file and parameters for Nanopore data analysis",
    responses={
        200: {
            "description": "Analysis started successfully",
            "content": {
                "application/json": {
                    "example": {
                        "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "status": "received",
                        "message": "Nanopore data processing started"
                    }
                }
            }
        },
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        500: {"description": "File processing error"}
    }
)
async def analyze_nanopore(
    fastq_file: Annotated[UploadFile, File(description="FASTQ file for analysis")],
    trim_first_bases: int = Form(80),
    trim_after_base: int = Form(700),
    min_quality: Optional[int] = Form(None),
    max_ambiguous: Optional[int] = Form(None),
    minlen: int = Form(150),
    maxns: int = Form(5),
    maxee: float = Form(2.0),
    classifier: str = Form("naive-bayes"),
    ref_seq: str = Form("silva"),
    ref_db: str = Form("gtdb"),
    additional_email: Optional[str] = Form(None),
    analysis_name: Optional[str] = Form(None),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process Nanopore sequencing data with the following steps:
    1. Validate user authentication
    2. Save uploaded FASTQ file
    3. Create analysis job record
    4. Return job information
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    try:
        job_id = str(uuid.uuid4())
        file_path = UPLOADS_DIR / f"{job_id}_{fastq_file.filename}"

        with open(file_path, "wb") as buffer:
            content = await fastq_file.read()
            buffer.write(content)

        # Prepare parameters as JSON
        params = {
            "trim_first_bases": trim_first_bases,
            "trim_after_base": trim_after_base,
            "min_quality": min_quality,
            "max_ambiguous": max_ambiguous,
            "minlen": minlen,
            "maxns": maxns,
            "maxee": maxee,
            "classifier": classifier,
            "reference_sequences": ref_seq,
            "reference_db": ref_db,
            "additional_email": additional_email,
            "analysis_name": analysis_name
        }

        db_job = AnalysisJob(
            job_id=job_id,
            user_id=1,
            type="nanopore",
            file_path=str(file_path),
            parameters=json.dumps(params),
            status="pending"
        )
        
        db.add(db_job)
        db.commit()
        db.refresh(db_job)

        return AnalysisResponse(
            job_id=job_id,
            status="received",
            message="Nanopore data processing started"
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )