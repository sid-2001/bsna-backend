from fastapi import APIRouter,status,HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession

from .services import ScheduleService
from .models import SupportSchedule
from .schemas import SupportScheduleBase,SupportScheduleCreate,SupportScheduleUpdate,SupportScheduleUser

from src.db.main import get_session
from src.auth.dependencies import AccessTokenBearer
from src.users.utils import check_auth_user,check_admin_user

schedule_router = APIRouter()
access_token_bearer = AccessTokenBearer()
schedule_service = ScheduleService()

@schedule_router.post("/", response_model=SupportScheduleBase, status_code=status.HTTP_201_CREATED)
async def create_new_schedule(schedule_data:SupportScheduleCreate,
                              session:AsyncSession = Depends(get_session),
                              user_details:dict = Depends(access_token_bearer)):
    try:
        if check_admin_user(user_details["user"]) is False:
            return HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden"
            )
        schedule = await schedule_service.create_new_schedule(session=session,schedule=schedule_data)
        if schedule is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to create schedule"
            )
        return schedule
    except Exception as e:
        print(f"Exception in creating schedule ::: {e}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )

@schedule_router.get("/", response_model=List[SupportScheduleUser], status_code=status.HTTP_200_OK)
async def get_all_schedules(session:AsyncSession = Depends(get_session),
                            user_details:dict = Depends(access_token_bearer)):
    try:
        if check_auth_user(user_details["user"]) is False:
            return HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden"
            )
        schedules = await schedule_service.get_all_schedules(session=session)
        if schedules is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedules not found"
            )
        return schedules
    except Exception as e:
        print(f"Exception in getting schedules ::: {e}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )