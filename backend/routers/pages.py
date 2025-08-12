from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from ..dependencies import get_optional_user, get_current_user
from typing import Dict, Any
from ..models.user import UserInDB
from typing import Optional

router = APIRouter()
BASE_DIR = Path(__file__).parent.parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

def get_base_context(
    request: Request, 
    current_user: Optional[UserInDB], 
    page_title: str, 
    active_tab: str
) -> Dict[str, Any]:
    """Создает базовый контекст для всех страниц"""
    return {
        "request": request,
        "page_title": page_title,
        "active_tab": active_tab,
        "user_authenticated": current_user is not None,
        "username": current_user.username if current_user else None,
        "email": current_user.email if current_user else None,
        "full_name": current_user.full_name if current_user else None
    }

@router.get(
    "/",
    name="index",
    response_class=HTMLResponse,
    tags=["Pages"],
    summary="Главная страница",
    description="Отображает главную страницу с информацией о сервисе и ссылками на формы анализа"
)
async def home(
    request: Request,
    current_user: Optional[UserInDB] = Depends(get_optional_user)
):
    context = get_base_context(
        request=request,
        current_user=current_user,
        page_title="Metabarcoding Data Analysis",
        active_tab="home"
    )
    return templates.TemplateResponse("pages/index.html", context)

@router.get(
    "/analysis/illumina",
    response_class=HTMLResponse,
    tags=["Pages"],
    summary="Форма загрузки данных Illumina",
    description="Отображает форму для загрузки и анализа данных Illumina"
)
async def illumina_page(
    request: Request,
    current_user: Optional[UserInDB] = Depends(get_optional_user)
):
    context = get_base_context(
        request=request,
        current_user=current_user,
        page_title="Illumina Sequencing",
        active_tab="illumina"
    )
    return templates.TemplateResponse("pages/illumina.html", context)

@router.get(
    "/analysis/nanopore",
    response_class=HTMLResponse,
    tags=["Pages"],
    summary="Форма загрузки данных Nanopore",
    description="Отображает форму для загрузки и анализа данных Nanopore"
)
async def nanopore_page(
    request: Request,
    current_user: Optional[UserInDB] = Depends(get_optional_user)
):
    context = get_base_context(
        request=request,
        current_user=current_user,
        page_title="Nanopore Sequencing",
        active_tab="nanopore"
    )
    return templates.TemplateResponse("pages/nanopore.html", context)