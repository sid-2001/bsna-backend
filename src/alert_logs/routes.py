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

@alert_router.get("/", response_model=List[AlertLogsBase], status_code=status.HTTP_200_OK)
async def get_all_logs(session:AsyncSession = Depends(get_session),
                       user_details: dict = Depends(access_token)):
    if(check_admin_user(user_details["user"]) is False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
    alerts = await alert_service.get_all_alerts(session=session)
    if alerts is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerts not found"
        )
    return alerts

@alert_router.get("/open", response_model=List[AlertLogsBase], status_code=status.HTTP_200_OK)
async def get_open_logs(session:AsyncSession = Depends(get_session),
                       user_details: dict = Depends(access_token)):
    if(check_auth_user(user_details["user"]) is False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
    alerts = await alert_service.get_open_alerts(session=session)
    if alerts is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerts not found"
        )
    return alerts

@alert_router.put("/close/{alert_id}", response_model=AlertLogsBase, status_code=status.HTTP_200_OK)
async def close_fixed_alert(alert_id: str,
                            session: AsyncSession = Depends(get_session),
                            user_details: dict = Depends(access_token),
                            ):
    if(check_auth_user(user_details["user"]) is False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
    closed_alert = await alert_service.close_alert(session=session, alert_id=alert_id, fixed_by=user_details["user"]["user_id"])
    if closed_alert is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to close alert"
        )
    return closed_alert
    