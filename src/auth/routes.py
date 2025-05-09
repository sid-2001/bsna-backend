
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime
from src.auth.dependencies import RefreshTokenBearer
from src.users.utils import create_access_token
from fastapi.websockets import WebSocket, WebSocketDisconnect

from manager import managerObj



active_connections: set[WebSocket] = set()


auth_router = APIRouter()

@auth_router.get("/refresh-token")
async def refresh_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details['exp']
    formatted_timestamp = datetime.fromtimestamp(expiry_timestamp)
    if(formatted_timestamp > datetime.now()):
        new_access_token = create_access_token(
            user_data=token_details['user']
        )
        return JSONResponse(
            content={
                "access_token": new_access_token
            },
            status_code=status.HTTP_200_OK
        )
    print(f"Timestamp :: {expiry_timestamp} :: formatted time :: {formatted_timestamp}")
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Token invalid / expired"
    )



async def send_periodic_messages():
    while True:
        await asyncio.sleep(2)  # Wait for 20 seconds
        for connection in active_connections:
            try:
                message = "This is a periodic notification from the server."
                await connection.send_text(message)
                print(f"Sent periodic message: {message}")
            except Exception as e:
                print(f"Error sending periodic message: {e}")

@auth_router.websocket("/ws/notifications")



async def websocket_endpoint(websocket: WebSocket):
  
    await managerObj.connect(websocket)
    

    while True:
        try:
            message = await websocket.receive_json()
            
            for client in managerObj.connected_clients:
                await managerObj.send_message(client, message)


        except WebSocketDisconnect:
            await managerObj.disconnect(websocket)
        




# async def websocket_endpoint(websocket: WebSocket):
#     # Accept the WebSocket connection
#     print("In My Notification Function")
#     print("in ws notificaiton")
#     await websocket.accept()
#     active_connections.add(websocket)
#     print("WebSocket connection established")  # Debug message


#     asyncio.create_task(send_periodic_messages())
    

#     try:
#         while True:
#             # Keep the connection alive
#             print("Trying to connect to webscoket")
#             await websocket.receive_text()
#     except WebSocketDisconnect:
#         active_connections.remove(websocket)
#         print("WebSocket connection closed")  # Debug message






# Broadcast a message to all connected clients
async def broadcast_message(message: str):
    
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except Exception as e:
            print(f"Error broadcasting message: {e}") 
    for connection in active_connections:
        await connection.send_text(message)

