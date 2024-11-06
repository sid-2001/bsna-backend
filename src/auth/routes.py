from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime
from src.auth.dependencies import RefreshTokenBearer
from src.users.utils import create_access_token

auth_router = APIRouter()

@auth_router.get("/refresh-token")
async def refresh_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details['exp']
    formatted_timestamp = datetime.fromtimestamp(expiry_timestamp)
    if(formatted_timestamp > datetime.now()):
        new_access_token = create_access_token(
            user_data=token_details['user']
        )
        return JSONResponse(
            content={
                "access_token": new_access_token
            },
            status_code=status.HTTP_200_OK
        )
    print(f"Timestamp :: {expiry_timestamp} :: formatted time :: {formatted_timestamp}")
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Token invalid / expired"
    )