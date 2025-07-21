from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from pathlib import Path
from ..dependencies import get_current_user
from ..models.user import UserCreate, UserInDB
from ..services.auth import register_user, authenticate_user
from ..services.jwt import create_access_token

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

# мне нужно будет везде поменять research на registration
# @router.get("/research")
@router.get("/register")
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

@router.post("/api/auth/register", response_model=UserInDB)
async def register(user_data: UserCreate):
    try:
        return register_user(user_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username
    }