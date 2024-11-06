from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select,insert,delete,update,asc
from typing import List, Optional
import uuid
from fastapi.responses import JSONResponse

from .schemas import AlertLogsBase,AlertLogsCreate,AlertLogsUpdate
from .models import AlertLogs
from src.drivers.service import DriverService
from src.drivers.schemas import DriverBase
from fastapi import HTTPException,status

driver_service = DriverService()

class AlertService :
    async def raise_alert(self, session:AsyncSession, alert_data:AlertLogsCreate) -> AlertLogs | None :
        try:
            driver_data = alert_data.model_dump()
            driver_found = await driver_service.get_driver_by_name(session=session, driver_name=driver_data["driver_name"])
            if driver_found is None :
                raise HTTPException(
                    status_code=404,
                    detail="Driver not found"
                )
            statement = select(AlertLogs).where(AlertLogs.driver_name == driver_data["driver_name"] and AlertLogs.status == "open")
            result = await session.exec(statement)
            alert_found = result.first()
            if alert_found is not None :
                print(f"Alert exists :: {alert_found}")
                alert_found.transaction_count = driver_data["transaction_count"]
                session.add(alert_found)
                await session.commit()
                # call firebase notification method
                return alert_found
            new_alert = AlertLogs(**driver_data)
            session.add(new_alert)
            await session.commit()
            # call firebase notification method
            return new_alert
        except HTTPException as http_exception:
            raise http_exception
        except Exception as e:
            print(f"Exception in raising alert ::: {e}")
            return None