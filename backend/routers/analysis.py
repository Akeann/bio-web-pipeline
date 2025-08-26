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

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

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
            "analysis_name": analysis_name,
            "original_filename": fastq_file.filename
        }

        # Create database record with REAL user ID
        db_job = AnalysisJob(
            job_id=job_id,
            user_id=current_user.id,  # Используем реальный ID пользователя
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
            "analysis_name": analysis_name,
            "original_filename": fastq_file.filename
        }

        # Используем реальный ID пользователя
        db_job = AnalysisJob(
            job_id=job_id,
            user_id=current_user.id,  # Используем реальный ID пользователя
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

# Дополнительные эндпоинты для работы с задачами анализа
@router.get(
    "/jobs",
    summary="Get user's analysis jobs",
    description="Returns list of analysis jobs for the current user"
)
async def get_user_jobs(
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    jobs = db.query(AnalysisJob).filter(
        AnalysisJob.user_id == current_user.id
    ).order_by(AnalysisJob.created_at.desc()).all()
    
    return {
        "jobs": [
            {
                "job_id": job.job_id,
                "type": job.type,
                "status": job.status,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "analysis_name": json.loads(job.parameters).get('analysis_name') if job.parameters else None
            }
            for job in jobs
        ]
    }

@router.get(
    "/jobs/{job_id}",
    summary="Get analysis job details",
    description="Returns detailed information about specific analysis job"
)
async def get_job_details(
    job_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    job = db.query(AnalysisJob).filter(
        AnalysisJob.job_id == job_id,
        AnalysisJob.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return {
        "job_id": job.job_id,
        "type": job.type,
        "status": job.status,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "parameters": json.loads(job.parameters) if job.parameters else {},
        "result_path": job.result_path
    }