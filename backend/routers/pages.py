from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from ..dependencies import get_current_user

router = APIRouter()
BASE_DIR = Path(__file__).parent.parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@router.get("/")
async def index(request: Request, current_user=Depends(get_current_user)):
    return templates.TemplateResponse(
        "pages/index.html",
        {
            "request": request,
            "page_title": "Metabarcoding Data Analysis",
            "active_tab": "home",
            "user_authenticated": current_user is not None,
            "username": current_user["username"] if current_user else None
        }
    )

@router.get("/illumina")
async def illumina_page(request: Request, current_user=Depends(get_current_user)):
    return templates.TemplateResponse(
        "pages/illumina.html",
        {
            "request": request,
            "page_title": "Illumina Sequencing",
            "active_tab": "illumina",
            "user_authenticated": current_user is not None,
            "username": current_user["username"] if current_user else None
        }
    )

@router.get("/nanopore")
async def nanopore_page(request: Request, current_user=Depends(get_current_user)):
    return templates.TemplateResponse(
        "pages/nanopore.html",
        {
            "request": request,
            "page_title": "Nanopore Sequencing",
            "active_tab": "nanopore",
            "user_authenticated": current_user is not None,
            "username": current_user["username"] if current_user else None
        }
    )

@router.get("/research")
async def research_page(request: Request, current_user=Depends(get_current_user)):
    return templates.TemplateResponse(
        "pages/research.html",
        {
            "request": request,
            "page_title": "Research Registration",
            "active_tab": "research",
            "user_authenticated": current_user is not None,
            "username": current_user["username"] if current_user else None
        }
    )