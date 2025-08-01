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

# Конфигурация путей
UPLOADS_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

@router.post(
    "/illumina",
    response_model=AnalysisResponse,
    summary="Запуск анализа Illumina",
    description="Принимает FASTQ файл и параметры для анализа данных Illumina",
    responses={
        200: {
            "description": "Анализ успешно запущен",
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
        401: {"description": "Не авторизован"},
        500: {"description": "Ошибка при обработке файла"}
    }
)
async def analyze_illumina(
    fastq_file: Annotated[UploadFile, File(description="FASTQ файл для анализа")],
    params: IlluminaAnalysis,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Генерация ID задачи
        job_id = str(uuid.uuid4())
        file_path = UPLOADS_DIR / f"{job_id}_{fastq_file.filename}"

        # Сохранение файла
        with open(file_path, "wb") as buffer:
            buffer.write(await fastq_file.read())

        # Создание записи в БД
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
    summary="Запуск анализа Nanopore",
    description="Принимает FASTQ файл и параметры для анализа данных Nanopore",
    responses={
        200: {
            "description": "Анализ успешно запущен",
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
        401: {"description": "Не авторизован"},
        500: {"description": "Ошибка при обработке файла"}
    }
)
async def analyze_nanopore(
    fastq_file: Annotated[UploadFile, File(description="FASTQ файл для анализа")],
    params: NanoporeAnalysis,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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