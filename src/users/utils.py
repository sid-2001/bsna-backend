from passlib.context import CryptContext
from datetime import timedelta, datetime
import jwt
from src.config import Config
import uuid
import logging

password_context = CryptContext(schemes=["bcrypt"])

JWT_EXPIRY = 3600

def generate_hash(password:str) -> str:
    return password_context.hash(password)

def verify_hash(password:str, hash:str) -> bool:
    return password_context.verify(password, hash)

# create jwt access tokens
def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False) -> str:
    
    payload = {
        "user": user_data,
        "exp": datetime.now() + (expiry if expiry is not None else timedelta(seconds=JWT_EXPIRY)),
        "jti": str(uuid.uuid4()),
        'refresh':refresh
    }
    
    token = jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET_KEY,
        algorithm=Config.JWT_ALGO
    )
    
    return token

# decode the token
def decode_token(token: str) -> dict:
    try:
        token_decoded = jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET_KEY,
            algorithms=[Config.JWT_ALGO]
        )
        return token_decoded
    except jwt.PyJWTError as err :
        logging.exception(err)
        return None
    except jwt.exceptions.ExpiredSignatureError as exp_err :
        logging.exception(f"Signature expried :: {exp_err}")
        return None
    
def check_admin_user(user_data: dict) -> bool:
    if user_data and user_data["role"] == "admin":
        return True
    else:
        return False
    
def check_auth_user(user_data: dict) -> bool:
    if user_data and (user_data["role"] == "admin" or user_data["role"] == "user"):
        return True
    else:
        return False