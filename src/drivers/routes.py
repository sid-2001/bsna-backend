from fastapi import APIRouter,status,HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession

from .schemas import DriverCreate,DriverBase,DriverUpdate,DriverUpdateCount,UserIDsRequest
from .service import DriverService
from src.db.main import get_session
from src.auth.dependencies import AccessTokenBearer
from src.users.utils import check_admin_user,check_auth_user


driver_router = APIRouter()
driver_service = DriverService()
access_token_bearer = AccessTokenBearer()

# @driver_router.get("/", response_model=List[DriverBase], status_code=status.HTTP_200_OK)
# async def get_all_drivers(
#     session: AsyncSession = Depends(get_session),
#     user_details: dict = Depends(access_token_bearer)
# ):
#     if not check_auth_user(user_details["user"]):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Unauthorized"
#         )
    
#     drivers = await driver_service.get_all_drivers(session=session)
    
#     if not drivers:
#         return JSONResponse(
#             content={"message": "Drivers not found or empty list"},
#             status_code=status.HTTP_200_OK
#         )

#     return drivers  # Now returns serialized Pydantic models

# @driver_router.get("/", response_model=List[DriverBase])
# async def get_drivers(session: AsyncSession = Depends(get_db)):
#     drivers = await driver_service.get_all_drivers(session)
    
#     if not drivers:
#         raise HTTPException(status_code=404, detail="No drivers found")

#     return drivers

@driver_router.get("/", response_model=List[DriverBase], status_code=status.HTTP_200_OK)
async def get_all_active_drivers(session: AsyncSession = Depends(get_session),
                                 user_details: dict = Depends(access_token_bearer)):
    # Check if the user is authorized
    if not check_auth_user(user_details["user"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
    
    # Fetch active drivers
    drivers = await driver_service.get_all_drivers(session)
    
    # Handle case where no active drivers exist
    if not drivers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active drivers found"
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
    drivers = await driver_service.update_transaction_count(session=session)
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


@driver_router.post("/driver/{driver_id}", status_code=status.HTTP_201_CREATED)
async def add_driver_with_users(
    driver_id: str, 
    user_ids_request: UserIDsRequest, 
    session: AsyncSession = Depends(get_session),
    user_details: dict = Depends(access_token_bearer)
):
    if check_admin_user(user_details["user"]) is False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    
    print(driver_id)
    print(user_ids_request.user_ids)
    added_users = await driver_service.add_users_to_driver(driver_id=driver_id, user_ids=user_ids_request.user_ids, session=session)
    if added_users is None:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Users not added to driver")

    return {"message": "Users added successfully", "driver_id": driver_id, "user_ids": user_ids_request.user_ids}


@driver_router.put("/driver/{driver_id}", status_code=status.HTTP_200_OK)
async def remove_users_from_driver(
    driver_id: str, 
    user_ids_request: UserIDsRequest, 
    session: AsyncSession = Depends(get_session),
    user_details: dict = Depends(access_token_bearer)
):
    if check_admin_user(user_details["user"]) is False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    removed_users = await driver_service.remove_users_from_driver(driver_id=driver_id, user_ids=user_ids_request.user_ids, session=session)
    if removed_users is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Users not removed from driver")

    return {"message": "Users removed successfully", "driver_id": driver_id, "user_ids": user_ids_request.user_ids}
