from fastapi import APIRouter,status,HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.auth.dependencies import AccessTokenBearer
from src.users.utils import check_admin_user, check_auth_user
from .schemas  import AlertLogsBase,AlertLogsCreate,AlertLogsUpdate
from .models import AlertLogs
from.services import AlertService

alert_router = APIRouter()
alert_service = AlertService()

access_token = AccessTokenBearer()

@alert_router.post("/", response_model=AlertLogsBase, status_code=status.HTTP_201_CREATED)
async def raise_alert(alert_data:AlertLogsCreate,
                      session: AsyncSession = Depends(get_session),
                      user_details: dict = Depends(access_token)):
    if(check_admin_user(user_details["user"]) is False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
    alert = await alert_service.raise_alert(session=session, alert_data=alert_data)
    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Alert not created"
        )
    return alert