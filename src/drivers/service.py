from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select,insert,delete,update,asc,desc,and_
from .schemas import DriverCreate,DriverBase,DriverUpdate,DriverUpdateCount
from src.drivers.models import Driver
from typing import List
import uuid
from fastapi import HTTPException
import datetime
import httpx

from src.config import Config

class DriverService:
    
    async def get_all_drivers(self,session:AsyncSession) -> List[DriverBase] | None:
        statement = select(Driver).where(Driver.is_Active == True).order_by(desc(Driver.name))
        result = await session.exec(statement=statement)
        drivers = result.all()
        return drivers
    
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
    
    async def get_drivers_from_mf(self) -> List|None :
        try:
            headers = {
                "Authorization":f"Bearer AAIgNDdiNDI3NDE1MGE0NDU4ZGM2ZjkyYWU2ZTc0NGU5YzZzEeRP5ZXQJXJ3NCiOQvWy8dZqhslGWho3gTlLOshfLyU71J77_dk1axr08pvIWyu0k1s9nCfMDp4PThJ6HRUhhAPM6pv42F5yoT0tnQeQNXKzD-f5cvLDX-yS4BEGPvqrrbQV8xU86WN2Oo4dgvcT",
                "X-Client-Certificate":"MIIEFzCCAv+gAwIBAgIUGCBGxxtA5bFka+JCHbvMqjLw7GkwDQYJKoZIhvcNAQELBQAwgbMxCzAJBgNVBAYTAklOMRAwDgYDVQQIDAdIYXJ5YW5hMREwDwYDVQQHDAhHdXJ1Z3JhbTErMCkGA1UECgwiSW1wcm9uaWNzIERpZ2l0ZWNoIFByaXZhdGUgTGltaXRlZDEQMA4GA1UECwwHRGlnaXRhbDEaMBgGA1UEAwwRd3d3LmltcHJvbmljcy5jb20xJDAiBgkqhkiG9w0BCQEWFWNvbnRhY3RAaW1wcm9uaWNzLmNvbTAeFw0yNDExMTgwOTAxMjNaFw0yNTExMTgwOTAxMjNaMIGzMQswCQYDVQQGEwJJTjEQMA4GA1UECAwHSGFyeWFuYTERMA8GA1UEBwwIR3VydWdyYW0xKzApBgNVBAoMIkltcHJvbmljcyBEaWdpdGVjaCBQcml2YXRlIExpbWl0ZWQxEDAOBgNVBAsMB0RpZ2l0YWwxGjAYBgNVBAMMEXd3dy5pbXByb25pY3MuY29tMSQwIgYJKoZIhvcNAQkBFhVjb250YWN0QGltcHJvbmljcy5jb20wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCi6t0Wj/rZhF2vb6AWM3ikFrFssKwYcqHVlkwAtu+YPTr0iuA0G8hdITOTf48TwpESXoawLe8ExhTFE8ya64XZBDyuriqtgjCkc0Xd4Arq7ebGso2N9Gdv+QCiogcdT2AYkmRpPVCGmcr0lhrrx7Shg3Vlm/TvrHDkyrHIon4zrUa/toycoYgEE7NwkSlykWjaAIJShxX9bPH7K+8R66KqL2MtSQakHVLoGOzfwaC+C1iNy0kTIbJGO+bhHAq0yJLFJpz37iYK65X1KitcmH8nfjCckQAMoq5F95NlPiLrKBKc6eXBnxoE4L+T5VeRPwOcRf0wRqy49X0VcCUKhf+vAgMBAAGjITAfMB0GA1UdDgQWBBSjIhc0bTkUz5n8MnBSFybz+tmC7zANBgkqhkiG9w0BAQsFAAOCAQEACdTJrQm1eMVXFY4RUOBY0/QDFo+HIIdomRgOwqxWw0SHOGAAXN8jJXVXmzqcyRdJtVDgnUEFei3SS/mKh7g82CESbhbj7e8qSr0BTyPhO5BlEIu72lyQk7DCO5DNlcWzlNKbd07uEaR3dm5LtHxS1ixLaF16LZY7xAGB1HIVU/esqW2p7GgsosGrgGGQ6lOi/b0t0xKWds1PEBwoItcRoKhwYkPGHws8RU8xYcAG74LhFEWA1MBO7e0Hdf90oY8noFt1ZQzoG8+yuYU2q/d5Jj1oKOBlLjR1XgQV/3GgXqYP7NRr8iRXKgMdA6M6ov4X09kndy6Ql6nnJrrRbyI9nQ==",
                "X-IBM-Client-Id":"47b4274150a4458dc6f92ae6e744e9c6",
                "X-IBM-Client-Secret":"1cb7583c6630a16ea267390f1794e37b"
            }
            url = Config.BOLSBSNA_URL
            async with httpx.AsyncClient() as client:
                response = await client.get(url=url, headers=headers)
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