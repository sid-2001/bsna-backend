from fastapi import APIRouter,status,HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import DriverCreate,DriverBase,DriverUpdate,DriverUpdateCount
from .service import DriverService
from src.db.main import get_session
from src.auth.dependencies import AccessTokenBearer
from src.users.utils import check_admin_user,check_auth_user

driver_router = APIRouter()
driver_service = DriverService()
access_token_bearer = AccessTokenBearer()

drivers_dummy = [
      {
         "driverName":"FXOM",
         "driverDescription":"MOBILE TO RFS TTO",
         "driverCount":0
      },
      {
         "driverName":"FQ08",
         "driverDescription":"COVER RATE ENQ'S",
         "driverCount":0
      },
      {
         "driverName":"FEE1",
         "driverDescription":"EE TO RFS",
         "driverCount":0
      },
      {
         "driverName":"TO12",
         "driverDescription":"TT VAL DATE ITEMS",
         "driverCount":1
      },
      {
         "driverName":"FAA3",
         "driverDescription":"PSL PAIN02 STATUS I",
         "driverCount":0
      },
      {
         "driverName":"FAA2\/5",
         "driverDescription":"PSL PAIN01 STATUS R",
         "driverCount":0
      },
      {
         "driverName":"FAA2\/5",
         "driverDescription":"PSL PAIN01 STATUS T",
         "driverCount":0
      },
      {
         "driverName":"FAA3",
         "driverDescription":"PSL PAIN02 STATUS T",
         "driverCount":0
      },
      {
         "driverName":"FXP1",
         "driverDescription":"RFS TO MT IPAY PROCESS",
         "driverCount":33
      },
      {
         "driverName":"FCHA",
         "driverDescription":"F.E.C. PENDING TRANS",
         "driverCount":0
      },
      {
         "driverName":"FNP6\/7",
         "driverDescription":"NPSI INWARD ZAPS",
         "driverCount":0
      },
      {
         "driverName":"",
         "driverDescription":"ENTRY_INTFC ITEMS PENDING",
         "driverCount":0
      },
      {
         "driverName":"",
         "driverDescription":"ENTRY_INTFC REJECTED ITMS",
         "driverCount":0
      },
      {
         "driverName":"FBPT",
         "driverDescription":"BOPCUST",
         "driverCount":0
      },
      {
         "driverName":"FXS6",
         "driverDescription":"STAFF TEMP LIMITS",
         "driverCount":0
      },
      {
         "driverName":"FXC4",
         "driverDescription":"CFC TRANSFERS",
         "driverCount":0
      },
      {
         "driverName":"FXI8",
         "driverDescription":"CALYPSO PAYMENTS",
         "driverCount":0
      },
      {
         "driverName":"SM96",
         "driverDescription":"SWIFT MESSAGES",
         "driverCount":0
      },
      {
         "driverName":"SB18",
         "driverDescription":"INCOMING SWIFT",
         "driverCount":1
      },
      {
         "driverName":"FXAI",
         "driverDescription":"INTEREST ENTRIES",
         "driverCount":0
      },
      {
         "driverName":"ITD2",
         "driverDescription":"AUTOMATED TT",
         "driverCount":0
      },
      {
         "driverName":"MQMT",
         "driverDescription":"SCRIPT TO MTFR",
         "driverCount":0
      },
      {
         "driverName":"FXA1",
         "driverDescription":"ZAPS SAP INTERFACE",
         "driverCount":0
      },
      {
         "driverName":"",
         "driverDescription":"IA PROCESSING (OLD)",
         "driverCount":0
      },
      {
         "driverName":"",
         "driverDescription":"RTGS PROCESSING (NEW)",
         "driverCount":0
      },
      {
         "driverName":"FXF7",
         "driverDescription":"F.E.C. MONEY TRANSFER",
         "driverCount":630
      },
      {
         "driverName":"TR20",
         "driverDescription":"ITRADE OUTWARD TT",
         "driverCount":0
      },
      {
         "driverName":"FXF0",
         "driverDescription":"F.E.C. AUTOMATION",
         "driverCount":6
      },
      {
         "driverName":"FCHD",
         "driverDescription":"PTT CHARGES",
         "driverCount":0
      },
      {
         "driverName":"FNP1",
         "driverDescription":"NPSI INWARD",
         "driverCount":0
      },
      {
         "driverName":"FAA4",
         "driverDescription":"RFS TO BPM WEBSERVICE",
         "driverCount":6
      },
      {
         "driverName":"SW04\/21",
         "driverDescription":"MT940 UNPROCESSED",
         "driverCount":0
      },
      {
         "driverName":"SW04\/21",
         "driverDescription":"MT950 UNPROCESSED",
         "driverCount":1326
      },
      {
         "driverName":"FXPM",
         "driverDescription":"PRISM TO RFS",
         "driverCount":0
      },
      {
         "driverName":"F705",
         "driverDescription":"QMAN TO RFS",
         "driverCount":0
      },
      {
         "driverName":"FXOM",
         "driverDescription":"FRAUD TRANSACTIONS MOBILE",
         "driverCount":0
      }
   ]

@driver_router.get("/",response_model=List[DriverBase],status_code=status.HTTP_200_OK)
async def get_all_drivers(
    session:AsyncSession = Depends(get_session),
    user_details:dict = Depends(access_token_bearer)):
    if check_auth_user(user_details["user"]) is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
    )
    drivers = await driver_service.get_all_drivers(session=session)
    if not drivers:
        return JSONResponse(
            content={
                "message":"Drivers not found or empty list"
            },
            status_code=status.HTTP_200_OK
        )
    return drivers

@driver_router.post("/", response_model=DriverBase, status_code=status.HTTP_201_CREATED)
async def create_driver(driver:DriverCreate, session:AsyncSession = Depends(get_session),
                        user_details = Depends(access_token_bearer)):
    if check_admin_user(user_details["user"]) is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )
    new_driver = await driver_service.create_driver(driver=driver, session=session)
    if new_driver is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver not created"
        )
    return new_driver

@driver_router.put("/{driver_uid}", response_model=DriverBase, status_code=status.HTTP_200_OK)
async def update_driver(driver_uid: str, driver:DriverUpdate, session:AsyncSession = Depends(get_session),
                        user_details:dict = Depends(access_token_bearer)):
    if check_admin_user(user_details["user"]) is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )
    updated_driver = await driver_service.update_driver_details(driver_uid=driver_uid,session=session,updated_driver=driver)
    if updated_driver is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver not updated"
        )
    return updated_driver

@driver_router.get("/refresh", response_model=List[DriverBase], status_code=status.HTTP_200_OK)
async def refresh_transaction_count(session:AsyncSession = Depends(get_session),
                                   user_details: dict = Depends(access_token_bearer)):
    if check_auth_user(user_details["user"]) is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
    # call for the api/method to get the txn counts
    drivers = await driver_service.update_transaction_count(session=session,drivers_to_update=drivers_dummy)
    if drivers is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No updates"
        )
    return drivers
    
@driver_router.put("/remove/{driver_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_driver(driver_uid:str,
                        session: AsyncSession = Depends(get_session),
                        user_details:dict = Depends(access_token_bearer)):
    if(check_admin_user(user_details["user"]) is False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action Forbidden"
    )
    deleted_driver = await driver_service.remove_driver_by_uid(driver_uid=driver_uid, session=session)
    if deleted_driver is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver not deleted"
        )
    