from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select,insert,delete,update,asc
from typing import List, Optional
import uuid

from .schemas import AlertLogsBase,AlertLogsCreate,AlertLogsUpdate
from .models import AlertLogs
from src.drivers.service import DriverService
from src.drivers.schemas import DriverBase
from fastapi import HTTPException
from fastapi import HTTPException

driver_service = DriverService()

class AlertService :
    async def raise_alert(self, session:AsyncSession, alert_data:AlertLogsCreate) -> AlertLogsBase | None :
        try:
            driver_data = alert_data.model_dump()
            driver_found = await driver_service.get_driver_by_name(session=session, driver_name=driver_data["driver_name"])
            if driver_found is None :
                raise HTTPException(
                    status_code=400,
                    detail="Driver not found"
                )
            new_alert = AlertLogs(**driver_data)
            session.add(new_alert)
            await session.commit()
            await session.refresh(new_alert)
            return new_alert
        except HTTPException as http_exception:
            raise http_exception
        except Exception as e:
            print(f"Exception in raising alert ::: {e}")
            return None