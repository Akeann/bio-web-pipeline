from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from pathlib import Path
from ..models.user import UserCreate, UserInDB
from ..services.auth import (
    register_user, 
    authenticate_user,
    oauth2_scheme,
    add_to_blacklist
)
from ..services.jwt import create_access_token
from fastapi import status

router = APIRouter()
BASE_DIR = Path(__file__).parent.parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@router.get(
    "/auth/login",
    response_class=HTMLResponse,
    tags=["Pages"],
    summary="Страница входа",
    description="Отображает форму для входа в систему"
)
async def login_page(request: Request):
    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
            "page_title": "Login",
            "active_tab": "login"
        }
    )

@router.get(
    "/auth/register",
    response_class=HTMLResponse,
    tags=["Pages"],
    summary="Страница регистрации",
    description="Отображает форму для регистрации нового пользователя"
)
async def register_page(request: Request):
    return templates.TemplateResponse(
        "auth/register.html",
        {
            "request": request,
            "page_title": "Register",
            "active_tab": "register"
        }
    )

@router.post(
    "/api/auth/login",
    tags=["Auth"],
    summary="Авторизация",
    description="Аутентификация пользователя и выдача JWT токена",
    response_model=UserInDB
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    access_token = create_access_token(data={"sub": user.username})
    
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=1800,
        secure=False,
        samesite="lax"
    )
    return response

@router.post(
    "/api/auth/register",
    tags=["Auth"],
    summary="Регистрация",
    description="Создание нового пользователя в системе",
    response_model=UserInDB
)
async def register(user_data: UserCreate):
    try:
        return register_user(user_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/auth/logout",
    tags=["Auth"],
    summary="Выход из системы",
    description="Завершает сеанс пользователя и очищает cookies"
)
async def logout(
    request: Request, 
    token: str = Depends(oauth2_scheme)
):
    response = RedirectResponse(url="/")
    
    # Получаем токен из куки, если не передан в заголовке
    if token is None:
        token = request.cookies.get("access_token")
        if token:
            token = token.strip('"').strip("'")
    
    if token:
        if token.startswith("Bearer "):
            token = token[7:]
        add_to_blacklist(token)
    
    response.delete_cookie("access_token")
    return response