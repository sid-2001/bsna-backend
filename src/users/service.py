from sqlmodel.ext.asyncio.session import AsyncSession
from src.users.schema import UserCreate, UserUpdate, UserLogin, User
from src.users.models import User
from sqlmodel import select,insert,delete,update,asc
from .utils import generate_hash,verify_hash,decode_token, create_access_token
from fastapi.responses import JSONResponse
from fastapi import status
from datetime import datetime, timedelta

class UserService:

    async def get_all_users(self,session:AsyncSession):
        statement = select(User).where(User.is_active == True).order_by(asc(User.user_code))
        result = await session.exec(statement)
        users = result.all()
        if users is not None:
            return users
        else:
            return None

    async def get_user_id(self,user_id:str,session:AsyncSession):
        statement = select(User).where(User.id == user_id)
        result = await session.exec(statement)
        user = result.first()
        if user is not None:
            return user
        else:
            return None

    async def get_user_by_code(self,user_code:str,session:AsyncSession):
        statement = select(User).where(User.user_code == user_code)
        result = await session.exec(statement)
        user = result.first()
        if user is not None:
            return user
        else:
            return None
        
    async def get_user_by_email(self,email:str,session:AsyncSession)-> User:
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        user = result.first()
        if user is not None:
            return user
        else:
            return None

    async def create_user(self, user:UserCreate, session:AsyncSession):
        try:
            new_user = User(**user.model_dump(exclude={'password'}))
            new_user.password_hash = generate_hash(user.password)
            session.add(new_user)
            await session.commit()
            return new_user
        except Exception as e:
            print(e)
            return None

    async def update_user(self, user_id:str, user:UserUpdate, session:AsyncSession):
        update_user = await self.get_user_id(user_id,session)
        if update_user is not None:
            update_user_dict = user.model_dump()
            for key, value in update_user_dict.items():
                setattr(update_user, key, value)
            session.add(update_user)
            await session.commit()
            return update_user
        else:
            return None

    async def delete_user(self, user_id:str, session:AsyncSession):
        user_to_delete = await self.get_user_id(user_id, session)
        if user_to_delete is not None:
            setattr(user_to_delete, "is_active",False)
            session.add(user_to_delete)
            await session.commit()
            return user_to_delete
        else:
            return None

    async def login_user(self, user:UserLogin, session:AsyncSession):
        userFound = await self.get_user_by_email(user.email, session)
        if userFound is not None:
            if verify_hash(user.password, userFound.password_hash):
                if user.notification_token is not None and user.notification_token != "" and len(user.notification_token) > 10:
                    userFound.notification_token = user.notification_token
                    session.add(userFound)
                    await session.commit()
                return userFound
            else:
                return None
        else:
            return None
        
    async def edit_user(self,user_id: str, user:UserUpdate, session:AsyncSession) -> User | None:
        user_found = await self.get_user_id(user_id=user_id, session=session)
        
        if user_found is not None:
            if user.first_name != "":
                user_found.first_name = user.first_name
            if user.last_name != "":
                user_found.last_name = user.last_name
            if user.email != "":
                user_found.email = user.email
            if user.phone != "":
                user_found.phone = user.phone
            if user.notification_token != "":
                user_found.notification_token = user.notification_token
            if user.user_code != "":
                user_found.user_code = user.user_code
                
            session.add(user_found)
            await session.commit()
            await session.refresh(user_found)  # Refresh to get the updated data from DB
            return user_found
        
        else:
            return None
        
        
    async def set_notification_token(self, session:AsyncSession, user_id:str, token:str) -> User | None:
        try:
            user_found = await self.get_user_id(user_id=user_id, session=session)
            if user_found is None:
                return JSONResponse(
                    content={
                        "message":"User not found"
                    },
                    status_code=status.HTTP_404_NOT_FOUND
                )
            if token is None or len(token) == 0:
                return JSONResponse(
                    content={
                        "message":"Token not provided"
                    },
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                
            user_found.notification_token = token
            session.add(user_found)
            await session.commit()
            return user_found
        except Exception as e:
            print(e)
            return JSONResponse(
                content={
                    "message":"Error setting notification token"
                },
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
    async def get_user_notification_tokens(self, session:AsyncSession):
        statement = select(User.notification_token).where(User.notification_token != None, User.notification_token != "")
        result = await session.exec(statement)
        tokens = result.all()
        if tokens is not None:
            return tokens
        else:
            return None
        