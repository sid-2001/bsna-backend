from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select,insert,delete,update,asc,or_,and_
from typing import List, Optional
import uuid
from fastapi.responses import JSONResponse
import datetime
from fastapi import HTTPException,status

from .schemas import AlertLogsBase,AlertLogsCreate,AlertLogsUpdate
from .models import AlertLogs
from src.drivers.service import DriverService
from src.users.service import UserService
from src.drivers.schemas import DriverBase,DriverUpdate
from src.firebase_config import FirebaseConfig

driver_service = DriverService()
user_service = UserService()
FB_Conf = FirebaseConfig()


class AlertService :
    
    # old notification  method not to be used as Pub-Sub is followed
    # async def send_alert_notification(self,title:str,body:str,session:AsyncSession):
    #     tokens_sequence = await user_service.get_user_notification_tokens(session=session)
    #     if tokens_sequence is None or tokens_sequence.count <= 0:
    #         return JSONResponse(
    #             content={
    #                 "message":"No tokens found!!"
    #             },
    #             status_code=status.HTTP_404_NOT_FOUND
    #         )
    #     FB_Conf.send_push_notifications(tokens_sequence)
        
    async def raise_alert(self, session:AsyncSession, alert_data:AlertLogsCreate) -> AlertLogs | None :
        try:


            # manager.send_message()
            driver_data = alert_data.model_dump()
            driver_found = await driver_service.get_driver_by_name(session=session, driver_name=driver_data["driverName"], driver_desc=driver_data['driverDescription'])
            if driver_found is None :
                raise HTTPException(
                    status_code=404,
                    detail="Driver not found"
                )
            statement = select(AlertLogs).where(and_(AlertLogs.driver_name == driver_data["driverName"], or_( AlertLogs.status == "open", AlertLogs.status == "attending") ))
            result = await session.exec(statement)
            alert_found = result.first()
            token_list=[]

            for user in driver_found.valid_users:
              found_user=await user_service.get_user_id(user,session=session)
              token_list.append(  found_user.notification_token)
            if alert_found is not None :
                print(f"Alert exists :: {alert_found}")
                alert_found.transaction_count = driver_data["driverCount"]
                session.add(alert_found)
                await session.commit()
                # call firebase notification method
                formatted_date = alert_found.raised_at.strftime("%Y-%m-%d %H:%M")
                title: str = f"{alert_found.driver_name} Failing since {formatted_date}"
                body: str = f"Transaction Count has reached {alert_found.transaction_count}"
                data = {
                   "name":driver_found.name,
                   "reason":alert_found.reason_of_abend,
                   "transaction_count":alert_found.transaction_count

                }
                if alert_found.attending_person is not None and alert_found.attending_person != "":
                    body += f"\nAttending Person: {alert_found.attendee.first_name}"
                
                # FB_Conf.send_push_notifications(tokens,title,body)

            
                notification_status = await FB_Conf.send_notification_to_users(title=title,body=body,token_list=token_list,data=data)
                print(f"Notification status ::: {notification_status}")
                
                updated_driver = DriverUpdate(
                name="",
                description="",
                is_Active=True,
                transaction_count= driver_data["driverCount"],
                updated_at=datetime.datetime.now()
                )
                await driver_service.update_driver_details(driver_uid=driver_found.uid,session=session,updated_driver=updated_driver)
                return alert_found
            new_alert = AlertLogs()
            new_alert.driver_name = driver_data["driverName"]
            new_alert.transaction_count = driver_data["driverCount"]

            
            new_alert.reason_of_abend = driver_data["abendCode"]
            session.add(new_alert)
            await session.commit()
            
            formatted_date = new_alert.raised_at.strftime("%Y-%m-%d %H:%M")
            title: str = f"{new_alert.driver_name} Failing since {formatted_date}"
            body: str = f"Transaction Count has reached {new_alert.transaction_count}"
            if new_alert.attending_person is not None and new_alert.attending_person != "":
                body += f"\nAttending Person: {new_alert.attendee.first_name}"
                
            # FB_Conf.send_push_notifications(tokens,title,body)
            notification_status = await FB_Conf.send_notification_to_users(title=title,body=body)
            print(f"Notification status ::: {notification_status}")
            
            updated_driver = DriverUpdate(
                name="",
                description="",
                is_Active=True,
                transaction_count=driver_data["driverCount"],
                updated_at=datetime.datetime.now()
            )
            await driver_service.update_driver_details(driver_uid=driver_found.uid,session=session,updated_driver=updated_driver)
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
            statement = select(AlertLogs).where(or_( AlertLogs.status == "open" , AlertLogs.status == "attending")).order_by(asc(AlertLogs.raised_at))
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
        
    async def attend_to_alert(self, alert_id: str, session:AsyncSession, attending_person:str) -> AlertLogs | None :
        try:
            statement = select(AlertLogs).where(AlertLogs.uid == alert_id)
            result = await session.exec(statement)
            alert_found = result.first()
            if alert_found is not None :
                if alert_found.attending_person is not None and alert_found.attending_person != "":
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={
                            "message":"Alert already attended"
                            }
                    )
                alert_found.attending_person = attending_person
                alert_found.status = "attending"
                session.add(alert_found)
                await session.commit()
                return alert_found
            else:
                return None
        except Exception as e:
            print(f"Exception in attending to alert ::: {e}")
            return JSONResponse(
                content={
                    "message":e.__cause__
                },
                status_code=status.HTTP_400_BAD_REQUEST
            )