from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select,insert,delete,update,asc,desc,and_
from src.users.schema import User
from .schemas import DriverCreate,DriverBase,DriverUpdate,DriverUpdateCount
from src.drivers.models import Driver
from typing import List
import uuid
from fastapi import HTTPException
import datetime
import httpx
from sqlalchemy.sql import text
from src.config import Config
import requests
class DriverService:
    
    # async def get_all_drivers(self,session:AsyncSession) -> List[DriverBase] | None:
    #     statement = select(Driver).where(Driver.is_Active == True).order_by(desc(Driver.name))
    #     print("i am here in this")
    #     print(statement)
    #     result = await session.exec(statement=statement)
    #     drivers = result.all()
    #     print(drivers)
    #     return drivers
    
  

    from sqlalchemy.sql import text

    from sqlalchemy.future import select
    from typing import List, Optional

    async def get_all_drivers(self, session: AsyncSession) -> Optional[List[DriverBase]]:
        statement = select(Driver).where(Driver.is_Active == True).order_by(desc(Driver.name))
        result = await session.execute(statement)
        drivers = result.scalars().all()  # Fetch ORM objects
        
        if not drivers:
            return None

        # Convert ORM models to Pydantic models using `model_dump()` (Pydantic v2) or `.dict()` (Pydantic v1)
        return [DriverBase(**{**driver.__dict__, "valid_users": driver.valid_users or []}) for driver in drivers]



    async def add_users_to_driver(self, driver_id: str, user_ids: list, session: AsyncSession):
     try:
        query = text("""
            UPDATE drivers 
            SET valid_users = array_cat(valid_users, ARRAY(
                SELECT unnest(CAST(:user_ids AS uuid[])) 
                EXCEPT 
                SELECT unnest(valid_users)
            )) 
            WHERE uid = :driver_id
        """)
        await session.execute(query, {"user_ids": user_ids, "driver_id": driver_id})
        await session.commit()
        return True
     except Exception as e:
        print(f"Error: {e}")
        await session.rollback()
        return None  
   
    # async def remove_users_from_driver(self, driver_id: str, user_ids: list, session: AsyncSession):
    #     try:
         
    #         driver = await session.get(Driver, driver_id)
    #         if not driver:
    #             return None

    #         users = await session.execute(select(User).filter(User.uid.in_(user_ids)))  # ✅ Fixed
    #         users = users.scalars().all()
    #         print(users)

    #         if not users:
    #             return None

    #         for user in users:
    #             if user in driver.users:
    #                 driver.users.remove(user)

    #         await session.commit()
    #         return users

    #     except Exception as e:
    #         await session.rollback()
    #         print(f"Error removing users from driver: {e}")
    #         return None


    async def remove_users_from_driver(self, driver_id: str, user_ids: list, session: AsyncSession):
        try:
            query = text("""
                UPDATE drivers 
                SET valid_users = ARRAY(
                    SELECT unnest(valid_users)
                    EXCEPT 
                    SELECT unnest(CAST(:user_ids AS uuid[]))
                )
                WHERE uid = :driver_id
            """)
            await session.execute(query, {"user_ids": user_ids, "driver_id": driver_id})
            await session.commit()
            return True
        except Exception as e:
            print(f"Error removing users from driver: {e}")
            await session.rollback()
            return None  
    


    async def get_driver_by_name(self, session:AsyncSession, driver_name:str, driver_desc:str = "") -> DriverBase | None:
        if driver_desc == "":
            statement = select(Driver).where(Driver.name == driver_name)
        else:
            statement = select(Driver).where(and_(Driver.name == driver_name, Driver.description == driver_desc))
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
    
    @staticmethod
    def get_forex_token():
        url = Config.O_AUTH_URL

        headers = {
            "X-IBM-Client-Id": Config.X_IBM_Client_Id,
            "X-IBM-Client-Secret": Config.X_IBM_Client_Secret,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "client_credentials",
            "scope": "forex"
        }
        
   
        try:
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                return response.json().get("access_token")
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return "sample_token"
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return "AAIgYjQ3MjVlYTYyNjFkOTMyODE5Yzc0ZWU1MjhmNjg3Yze4SrTzht9HXBYdjhD4fPwld6CIzPvAd2GwlXAtZ2R4kjEnJnEV27rm1z96Z4CAlCapq5_f7SOcykCcKiIlPjKXA1prU78hEUOotijuLcs6V9vuwJYxAlKspIlj96L7eAYxWS83xx2l3nQqzlh673mkyyzYUZUMGk3088zyfEG03fzkePew8UIwWNWcwI41vX4puGMWwIj8FuT9ICMB-dX0"


    async def get_drivers_from_mf(self) -> List|None :
        try:

            self.get_forex_token()
            headers = {
               "Authorization": f"Bearer {self.get_forex_token()}",

                "X-Client-Certificate":Config.X_Client_Certificate,
                "X-IBM-Client-Id":Config.X_IBM_Client_Id,
                "X-IBM-Client-Secret":Config.X_IBM_Client_Secret
            }
            
            url = Config.BOLSBSNA_URL
           
            async with httpx.AsyncClient() as client:
                response = await client.get(url=url, headers=headers)
                print(response.status_code)
                if response.status_code == 200:
                    data = response.json()
                    return data["drivers"]
                else:
                    print(f"Error in getting drivers from MF ::: {response}")
                    return None
        except Exception as e:
            print(f"Exception in getting drivers from MF ::: {e}")
            return None    
    
    async def update_transaction_count(self, session:AsyncSession) -> List[DriverBase] | None:
        try:
            drivers_to_update = await self.get_drivers_from_mf()
            additional_drivers = {}
            for driver_to_update in drivers_to_update:
                driver_found = await self.get_driver_by_name(session=session, driver_name=driver_to_update["driverName"], driver_desc=driver_to_update["driverDescription"])
                if driver_found is not None :
                    driver_found.transaction_count = driver_to_update["driverCount"]
                    session.add(driver_found)
                    await session.commit()
                else:
                    new_driver = DriverCreate(
                        name=driver_to_update["driverName"],
                        description=driver_to_update["driverDescription"],
                        valid_users=driver_to_update["valid_users"],
                    
                        
                        is_Active=True,
                        transaction_count=driver_to_update["driverCount"]
                    )
                    await self.create_driver(session=session, driver=new_driver)
                    additional_drivers[driver_to_update["driverName"]] = driver_to_update["driverCount"]
            drivers = await self.get_all_drivers(session=session)
            print(f"additional_drivers ::: {additional_drivers}")
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