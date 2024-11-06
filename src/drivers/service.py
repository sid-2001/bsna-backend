from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select,insert,delete,update,asc
from .schemas import DriverCreate,DriverBase,DriverUpdate,DriverUpdateCount
from src.drivers.models import Driver
from typing import List
import uuid
from fastapi import HTTPException

class DriverService:
    
    async def get_all_drivers(self,session:AsyncSession) -> List[DriverBase] | None:
        statement = select(Driver).order_by(asc(Driver.name))
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
        
    async def update_driver_details(self, session:AsyncSession, updated_driver:DriverUpdate) -> DriverBase | None:
        driver_found = await self.get_driver_by_name(session=session, driver_name=updated_driver.name)
        if driver_found is not None:
            driver_found_dict = updated_driver.model_dump()
            for key, value in driver_found_dict.items():
                setattr(driver_found, key, value)
            session.add(driver_found)
            await session.commit()
            await session.refresh(driver_found)
            return driver_found
        return None
    
    async def update_transaction_count(self, session:AsyncSession, drivers_to_update:List[DriverUpdateCount]) -> List[DriverBase] | None:
        try:
            for driver_to_update in drivers_to_update:
                driver_found = await self.get_driver_by_uid(session=session, driver_uid=driver_to_update.uid)
                if driver_found is not None:
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