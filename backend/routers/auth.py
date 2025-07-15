from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from ..dependencies import get_current_user

router = APIRouter()
BASE_DIR = Path(__file__).parent.parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@router.get("/logout")
async def logout():
    return RedirectResponse(url="/")

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
            "page_title": "Login",
            "active_tab": None
        }
    )

@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse(
        "auth/register.html",
        {
            "request": request,
            "page_title": "Register",
            "active_tab": None
        }
    )

@router.get("/profile")
async def profile_page(request: Request, current_user=Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse(
        "auth/profile.html",
        {
            "request": request,
            "page_title": "My Profile",
            "active_tab": "profile",
            "user": current_user
        }
    )