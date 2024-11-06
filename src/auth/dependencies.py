from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi import Request, status
from fastapi.exceptions import HTTPException
from src.users.utils import decode_token

class TokenBearer(HTTPBearer):
    
    def __init__(self, auto_error = True):
        super().__init__( auto_error=auto_error)
        
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        
        token = creds.credentials
        token_data = decode_token(token=token)
        if not self.token_valid(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token or expired token."
            )
            
        self.verify_token_data(token_data=token_data)
        
        return token_data
        
    
    def token_valid(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        payload = decode_token(jwtoken)

        if payload:
            isTokenValid = True

        return isTokenValid
    
    def verify_token_data(self, token_data:dict):
        raise NotImplementedError("Please implement this method in the subclass.")
    
    
class AccessTokenBearer(TokenBearer):
    
    def verify_token_data(self,token_data:dict):
        if token_data and token_data['refresh']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an access token"
            )

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self,token_data:dict):
        if token_data and not token_data['refresh']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an refresh token"
            )