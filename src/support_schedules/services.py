from typing import Optional, List

from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select,insert,delete,update,asc,desc,or_,and_
from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi import HTTPException,status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from src.users.models import User

from sqlalchemy.orm import aliased
from .schemas import SupportScheduleBase,SupportScheduleCreate,SupportScheduleUpdate,SupportScheduleUser
from .models import SupportSchedule, UserScheduleLink

class ScheduleService:

    async def create_new_schedule(self, session:AsyncSession, schedule:SupportScheduleCreate) -> SupportSchedule | None:
        try:
            print("new schedule creting")
        

            conflicting_users=[]
            for user_id in schedule.users or []:
                conflicting_schedule=await session.exec(

                   select(SupportSchedule).join(UserScheduleLink,SupportSchedule.uid==UserScheduleLink.schedule_id).where(
                    and_(
                        UserScheduleLink.user_id == user_id,
                        or_(
                            and_(
                                SupportSchedule.start_date <= schedule.start_date,
                                SupportSchedule.end_date >= schedule.start_date,
                            ),
                            and_(
                                SupportSchedule.start_date <= schedule.end_date,
                                SupportSchedule.end_date >= schedule.end_date,
                            ),
                            and_(
                                schedule.start_date <= SupportSchedule.start_date,
                                schedule.end_date >= SupportSchedule.end_date,
                            ),
                        ),
                    )

                ))
                if conflicting_schedule.first():
                 conflicting_users.append(user_id)

            if conflicting_users:
                return JSONResponse(
                    content={
                        "detail": "Schedule conflicts found for users",
                        "conflicting_users": conflicting_users,
                    },
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            
            schedule_found = await self.get_duplicate_schedule(session=session,schedule=schedule)
            new_schedule = SupportSchedule(**schedule.model_dump())
            if schedule_found is not None:
                return JSONResponse(
                    content=schedule_found,
                    status_code=status.HTTP_200_OK
                )
            session.add(new_schedule)
            await session.commit()
            await session.refresh(new_schedule)


            user_schedule_links = [
            UserScheduleLink(user_id=user_id, schedule_id=new_schedule.uid)
            for user_id in schedule.users or []
            ]
            session.add_all(user_schedule_links)
            await session.commit()



            return new_schedule
        
 

        except Exception as e:
            await session.rollback()
            print(f"Exception in adding schedule ::: {e}")
            raise e
        
  
  
  
    async def get_duplicate_schedule(self, session:AsyncSession, schedule:SupportScheduleCreate) -> SupportSchedule | None:
        try:
            statement = select(SupportSchedule).where(and_(SupportSchedule.start_date == schedule.start_date , SupportSchedule.end_date == schedule.end_date))
            result = await session.exec(statement=statement)
            schedule_found = result.first()
            if schedule_found is not None:
                return schedule_found
            return None
        except Exception as e:
            print(f"Exception in getting schedule ::: {e}")
            raise e
        
    async def get_schedule_by_uid(self, session:AsyncSession, schedule_uid:str) -> SupportSchedule | None:
        try:
            statement = select(SupportSchedule).where(SupportSchedule.uid == schedule_uid)
            result = await session.exec(statement=statement)
            schedule = result.first()
            if schedule is not None:
                return schedule
            return None
        except Exception as e:
            print(f"Exception in getting schedule ::: {e}")
            raise e
        
    async def get_schedule_by_start_date(self, session:AsyncSession, start_date:datetime) -> SupportSchedule | None:
        try:
            statement = select(SupportSchedule).where(SupportSchedule.start_date == start_date)
            result = await session.exec(statement=statement)
            schedule = result.first()
            if schedule is not None:
                return schedule
            return None
        except Exception as e:
            print(f"Exception in getting schedule ::: {e}")
            raise e

    async def get_schedule_by_end_date(self, session:AsyncSession, end_date:datetime) -> SupportSchedule | None:
        try:
            statement = select(SupportSchedule).where(SupportSchedule.end_date == end_date)
            result = await session.exec(statement=statement)
            schedule = result.first()
            if schedule is not None:
                return schedule
            return None
        except Exception as e:
            print(f"Exception in getting schedule ::: {e}")
            raise e


    async def get_users_in_date_range(
    self, session: AsyncSession, start_date: datetime, end_date: datetime
) -> List[dict]:
     try:
        # Fetch schedules overlapping with the date range
        schedule_stmt = select(SupportSchedule.uid).where(
            SupportSchedule.start_date <= end_date,
            SupportSchedule.end_date >= start_date
        )
        schedule_result = await session.exec(schedule_stmt)
        schedule_ids = schedule_result.all()  # This will be a list of UUIDs

        if not schedule_ids:
            return []  # No schedules found within the date range

        # Fetch user IDs linked to the schedules
        user_link_stmt = select(UserScheduleLink.user_id).where(
            UserScheduleLink.schedule_id.in_(schedule_ids)  # Directly use UUIDs
        )
        user_link_result = await session.exec(user_link_stmt)
        user_ids = user_link_result.all()  # This will also be a list of UUIDs

        if not user_ids:
            return []  # No users linked to the schedules

        # Fetch user details for the linked user IDs
        user_stmt = select(User).where(
            User.id.in_(user_ids)  # Directly use UUIDs
        )
        user_result = await session.exec(user_stmt)
        users = user_result.all()  # This will return a list of User objects

        # Format the users for the response
        return [
            {
                "id": user.id,
                "user_code": user.user_code,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": user.phone,
                "role": user.role,
            }
            for user in users
        ]

     except SQLAlchemyError as e:
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch users for the given date range."
        )
     except Exception as e:
        print(f"Error in fetching users: {e}")
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred."
        )



    async def get_all_schedules(self, session: AsyncSession):
     try:
        # Fetch all schedules
        schedule_stmt = select(SupportSchedule).order_by(SupportSchedule.start_date.desc())
        schedule_result = await session.execute(schedule_stmt)
        schedules = schedule_result.scalars().all()

        # Prepare the final result
        schedule_list = []
        for schedule in schedules:
            # Fetch all user IDs for the current schedule
            user_link_stmt = select(UserScheduleLink.user_id).where(UserScheduleLink.schedule_id == schedule.uid)
            user_link_result = await session.execute(user_link_stmt)
            user_ids = user_link_result.scalars().all()

            # Fetch user details for the obtained user IDs
            user_stmt = select(User).where(User.id.in_(user_ids))
            user_result = await session.execute(user_stmt)
            users = user_result.scalars().all()

            # Add schedule and its users to the final result
            schedule_list.append({
                "uid": schedule.uid,
                "start_date": schedule.start_date,
                "end_date": schedule.end_date,
                "environment": schedule.environment,
                "created_at": schedule.created_at,
                "users": [
                    {
                        "id": user.id,
                        "user_code": user.user_code,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email,
                        "phone": user.phone,
                        "role": user.role,
                    }
                    for user in users
                ]
            })

        return schedule_list

     except SQLAlchemyError as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch schedules.")
     except Exception as e:
        print(f"Error in fetching schedules: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
       