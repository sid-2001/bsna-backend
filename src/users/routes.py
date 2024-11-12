from src.users.service import UserService
from src.db.main import get_session
from fastapi import APIRouter, Depends, status, Header
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.users.schema import User, UserCreate, UserLogin, UserUpdate, UserAlerts
from typing import List
from .utils import decode_token, create_access_token, check_admin_user
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from src.auth.dependencies import AccessTokenBearer

user_router = APIRouter()

# create service object
user_service = UserService()

access_token_bearer = AccessTokenBearer()

# get all books
@user_router.get("/all",status_code=status.HTTP_200_OK, response_model=List[User])
async def get_all_users(session:AsyncSession = Depends(get_session), 
                        user_details = Depends(access_token_bearer)):
    if check_admin_user(user_details["user"]) is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
    users = await user_service.get_all_users(session=session)
    if users is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found"
        )
    return users

@user_router.post("/new", status_code=status.HTTP_201_CREATED, response_model=User)
async def create_user(user:UserCreate, session:AsyncSession = Depends(get_session),
                      user_details = Depends(access_token_bearer)
                    ):
    if check_admin_user(user_details["user"]) is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
    new_user = await user_service.create_user(user=user, session=session)
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not created"
        )
    return new_user

@user_router.put("/{user_id}", status_code=status.HTTP_200_OK, response_model=User)
async def update_user_by_id(user_id:str, user:UserUpdate, session:AsyncSession = Depends(get_session),
                      user_details = Depends(access_token_bearer)):
    if check_admin_user(user_details["user"]) is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
    updated_user = await user_service.update_user(user_id=user_id, user=user, session=session)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user

@user_router.get("/id/{user_id}", status_code=status.HTTP_200_OK, response_model=UserAlerts)
async def get_user_by_id(user_id:str, session:AsyncSession = Depends(get_session)):
    user = await user_service.get_user_id(user_id=user_id, session=session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@user_router.get("/code/{user_code}", status_code=status.HTTP_200_OK, response_model=UserAlerts)
async def get_user_by_user_code(user_code:str, session:AsyncSession = Depends(get_session)):
    user = await user_service.get_user_by_code(user_code=user_code, session=session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id:str, session:AsyncSession = Depends(get_session),
                      user_details = Depends(access_token_bearer)):
    if check_admin_user(user_details["user"]) is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
    user = await user_service.delete_user(user_id=user_id, session=session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@user_router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(user:UserLogin, session:AsyncSession = Depends(get_session)):
    userFound = await user_service.login_user(user=user, session=session)
    if userFound is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    user_data = {
                    "email":userFound.email,
                    "user_id": str(userFound.id),
                    "role": userFound.role
                }
    access_token = create_access_token(user_data=user_data)
    refresh_token = create_access_token(
                    user_data=user_data,
                    expiry=timedelta(days=1),
                    refresh=True
                    )
    return JSONResponse(
                    content={
                        "message":"Login success",
                        "access_token":access_token,
                        "refresh_token":refresh_token,
                        "user":user_data
                    },
                    status_code=status.HTTP_200_OK
                )