from datetime import datetime
from fastapi import APIRouter, Query,status,HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
import pdb
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
    
@schedule_router.get("/user", response_model=List[dict], status_code=status.HTTP_200_OK)
async def get_schedules_with_users(
    start_date: datetime = Query(..., description="The start date of the range"),
    end_date: datetime = Query(..., description="The end date of the range"),
    shift:str= Query(..., description="The shift of the range"),
    session: AsyncSession = Depends(get_session)  # Assuming get_session provides the AsyncSession
):   
    try:
        # Call the service method to fetch users in the date range
        data = await schedule_service.get_users_in_date_range(session=session, start_date=start_date, end_date=end_date ,shift=shift)
        # session.expire(session)
        return data
    except HTTPException as e:
      
        raise e
    except Exception as e:
      
        print(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching schedules and users."
        )


@schedule_router.put("/{id}", response_model=SupportScheduleBase, status_code=status.HTTP_201_CREATED)
async def update_schedule(id,schedule_data:SupportScheduleCreate,
                              session:AsyncSession = Depends(get_session),
                              user_details:dict = Depends(access_token_bearer)):
    try:
     
        if check_admin_user(user_details["user"]) is False:
            return HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,

                detail="Forbidden"
            )
        schedule = await schedule_service.update_schedule(session=session,schedule_id=id,updated_schedule=schedule_data)
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



@schedule_router.delete("/{id}", response_model=SupportScheduleBase, status_code=status.HTTP_201_CREATED)
async def update_schedule(id,
                              session:AsyncSession = Depends(get_session),
                              user_details:dict = Depends(access_token_bearer)):
    try:
     
        if check_admin_user(user_details["user"]) is False:
            return HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,

                detail="Forbidden"
            )
        schedule = await schedule_service.delete_schedule(session=session,schedule_id=id)
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


@schedule_router.delete("/{id}/user/{user_id}", response_model=SupportScheduleBase, status_code=status.HTTP_201_CREATED)
async def delete_schedule(id,user_id,
                              session:AsyncSession = Depends(get_session),
                              user_details:dict = Depends(access_token_bearer)):
    try:
     
        if check_admin_user(user_details["user"]) is False:
            return HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,

                detail="Forbidden"
            )
        schedule = await schedule_service.delete_user_from_schedule(session=session,schedule_id=id,user_id=user_id)
        if schedule is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to delete schedule"
            )
        return schedule
    except Exception as e:
        print(f"Exception in deletion schedule ::: {e}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )
