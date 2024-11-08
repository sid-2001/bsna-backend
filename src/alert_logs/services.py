from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select,insert,delete,update,asc
from typing import List, Optional
import uuid
from fastapi.responses import JSONResponse
import datetime
from fastapi import HTTPException,status

from .schemas import AlertLogsBase,AlertLogsCreate,AlertLogsUpdate
from .models import AlertLogs
from src.drivers.service import DriverService
from src.drivers.schemas import DriverBase
from src.firebase_config import FirebaseConfig

driver_service = DriverService()
FB_Conf = FirebaseConfig()

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
                tokens = ['fpDyPeywSQ6ZFok3lijECk:APA91bHq6pzt3Y9LjpWt8tUcRcn2vsYBZSoSzmzs2BqVYtdrjBJ1AEI82jv-PRUZ42Oro5FtO7KYyOQPwbGcBkvbvxw8c0leRv1ZDRf5taQ23vYUMhvupvk',
                        'c5kA8RFnQ0aZb_C-00K6Ls:APA91bEng4mMh0MU7uEY65w-P97yUJnwI5lYxe6zDiegcJz8g24AkYUA-e_gEjDy3Sbx751q_heaGbrv1Wx2tNWUt2g2Gpdfsdj158s8G6kaUyd5Cmvxj2E']
                title: str = "Demo Test BSNA"
                body: str = "Demo Body BSNA"
                print(f"tokens ::: {tokens} ::: type :::: {type(tokens)}")
                FB_Conf.send_push_notifications(tokens,title,body)
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
        
    async def get_all_alerts(self, session:AsyncSession) -> List[AlertLogs] | None :
        try:
            statement = select(AlertLogs).order_by(asc(AlertLogs.raised_at))
            result = await session.exec(statement)
            alerts = result.all()
            return alerts
        except Exception as e:
            print(f"Exception in getting all alerts ::: {e}")
            return None
        
    async def get_open_alerts(self, session:AsyncSession) -> List[AlertLogs] | None :
        try:
            statement = select(AlertLogs).where(AlertLogs.status == "open").order_by(asc(AlertLogs.raised_at))
            result = await session.exec(statement)
            alerts = result.all()
            return alerts
        except Exception as e:
            print(f"Exception in getting all open alerts ::: {e}")
            return None
        
    async def close_alert(self,session:AsyncSession, alert_id:str, fixed_by:str) -> AlertLogs | None :
        try:
            statement = select(AlertLogs).where(AlertLogs.uid == alert_id)
            result = await session.exec(statement)
            alert_found = result.first()
            if alert_found is not None :
                alert_found.status = "closed"
                alert_found.attending_person = fixed_by
                alert_found.fixed_at = datetime.datetime.now()
                session.add(alert_found)
                await session.commit()
                return alert_found
            else:
                return None
        except Exception as e:
            print(f"Exception in closing alert ::: {e}")
            return None