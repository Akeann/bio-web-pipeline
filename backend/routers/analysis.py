from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import uuid
from typing import Annotated
from sqlalchemy.orm import Session
from ..models.analysis import IlluminaAnalysis, NanoporeAnalysis, AnalysisResponse
from ..models.db_models import AnalysisJob, User
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
    params: IlluminaAnalysis,
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
            buffer.write(await fastq_file.read())

        # Create database record
        db_job = AnalysisJob(
            job_id=job_id,
            user_id=current_user.id,
            type="illumina",
            file_path=str(file_path),
            parameters=params.model_dump_json(),
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
            status_code=500,
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
    params: NanoporeAnalysis,
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
    try:
        job_id = str(uuid.uuid4())
        file_path = UPLOADS_DIR / f"{job_id}_{fastq_file.filename}"

        with open(file_path, "wb") as buffer:
            buffer.write(await fastq_file.read())

        db_job = AnalysisJob(
            job_id=job_id,
            user_id=current_user.id,
            type="nanopore",
            file_path=str(file_path),
            parameters=params.model_dump_json(),
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
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )