from typing import Optional, List
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select,insert,delete,update,asc,desc,or_,and_
from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi import HTTPException,status

from .schemas import SupportScheduleBase,SupportScheduleCreate,SupportScheduleUpdate,SupportScheduleUser
from .models import SupportSchedule

class ScheduleService:

    async def create_new_schedule(self, session:AsyncSession, schedule:SupportScheduleCreate) -> SupportSchedule | None:
        try:
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
            return new_schedule
        except Exception as e:
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
        
    async def get_all_schedules(self, session:AsyncSession) -> List[SupportSchedule] | None:
        try:
            statement = select(SupportSchedule).order_by(desc(SupportSchedule.start_date))
            result = await session.exec(statement=statement)
            schedules = result.all()
            if schedules is not None:
                return schedules
            return schedules
        except Exception as e:
            print(f"Exception in getting all schedules ::: {e}")
            raise e