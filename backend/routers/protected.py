from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import get_current_user
from ..models.user import UserInDB

router = APIRouter()

@router.get("/me", response_model=UserInDB)
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return current_user

@router.get("/items")
async def read_private_items(current_user: UserInDB = Depends(get_current_user)):
    return {"message": "Secret data", "owner": current_user.username}