from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select,insert,delete,update,asc,desc
from .schemas import DriverCreate,DriverBase,DriverUpdate,DriverUpdateCount
from src.drivers.models import Driver
from typing import List
import uuid
from fastapi import HTTPException
import datetime

class DriverService:
    
    async def get_all_drivers(self,session:AsyncSession) -> List[DriverBase] | None:
        statement = select(Driver).where(Driver.is_Active == True).order_by(desc(Driver.name))
        result = await session.exec(statement=statement)
        drivers = result.all()
        return drivers
    
    async def get_driver_by_name(self, session:AsyncSession, driver_name:str) -> DriverBase | None:
        statement = select(Driver).where(Driver.name == driver_name)
        result = await session.exec(statement=statement)
        driver = result.first()
        if driver is None:
            return None
        return driver
    
    async def get_driver_by_uid(self, session:AsyncSession, driver_uid:uuid.UUID) -> DriverBase | None:
        statement = select(Driver).where(Driver.uid == driver_uid)
        result = await session.exec(statement=statement)
        driver = result.first()
        if driver is None:
            return None
        return driver
    
    async def create_driver(self, session:AsyncSession, driver:DriverCreate) -> DriverBase | None:
        try:
            new_driver = Driver(**driver.model_dump())
            session.add(new_driver)
            await session.commit()
            await session.refresh(new_driver)
            return new_driver
        except Exception as e:
            print(f"Exception in adding driver ::: {e}")
            return None
        
    async def update_driver_details(self, driver_uid:str, session:AsyncSession, updated_driver:DriverUpdate) -> Driver | None:
        driver_found = await self.get_driver_by_uid(session=session, driver_uid=driver_uid)
        if driver_found is not None and driver_found.is_Active:
            if(updated_driver.name != "" and len(updated_driver.name) >= 4):
                driver_found.name = updated_driver.name
            if(updated_driver.description != "" and len(updated_driver.description) >= 1):
                driver_found.description = updated_driver.description
            if(updated_driver.transaction_count > 0 and updated_driver != driver_found.transaction_count):
                driver_found.transaction_count = updated_driver.transaction_count
            if(updated_driver.is_Active != None and updated_driver.is_Active != driver_found.is_Active):
                driver_found.is_Active = updated_driver.is_Active
            driver_found.updated_at = datetime.datetime.now()
            session.add(driver_found)
            await session.commit()
            await session.refresh(driver_found)
            return driver_found
        return None
    
    async def update_transaction_count(self, session:AsyncSession, drivers_to_update:List[DriverUpdateCount]) -> List[DriverBase] | None:
        try:
            for driver_to_update in drivers_to_update:
                driver_found = await self.get_driver_by_uid(session=session, driver_uid=driver_to_update.uid)
                if driver_found is not None and driver_found.is_Active :
                    driver_found.transaction_count = driver_to_update.transaction_count
                    session.add(driver_found)
                    await session.commit()
                else:
                    raise Exception("Driver not found")
            drivers = await self.get_all_drivers(session=session)
            return drivers
        except Exception as e:
            print(f"Exception in updating transaction count ::: {e}")
            return None
        
    async def remove_driver_by_uid(self,driver_uid:str, session:AsyncSession) -> Driver | None:
        try:
            driver_found = await self.get_driver_by_uid(session=session, driver_uid=driver_uid)
            if driver_found is not None:
                driver_found.is_Active = False
                session.add(driver_found)
                await session.commit()
                return driver_found
            return None
        except Exception as e:
            print(f"Exception in removing driver ::: {e}")
            return None