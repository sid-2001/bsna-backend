import firebase_admin
import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from firebase_admin import credentials, messaging
from typing import List, Optional
import httpx
from fastapi.exceptions import HTTPException
from src.config import Config

from manager import managerObj

class FirebaseConfig():
    
    
    def get_access_token(self) -> str | None:
        SERVICE_ACCOUNT_FILE = Config.SERVICE_KEY_FILE
        SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']
        
        credentials = service_account.Credentials.from_service_account_file(
                        SERVICE_ACCOUNT_FILE, scopes=SCOPES
                        )
        auth_request = Request()
        credentials.refresh(auth_request)
        access_token = credentials.token

        return access_token
    
    async def send_notification_to_users(self, title:str, body:str, data:dict = None):
        try:


            for client in managerObj.connected_clients:
                   
                    await managerObj.send_message(client, title)

            # access_token = self.get_access_token()
            # print(f"Access Token ::: {access_token}")
            # if access_token is None:
            #     raise Exception
            # message = {
            #     "message": {
            #         "topic": "Alerts",
            #         "notification": {
            #             "title": title,
            #             "body": body
            #         }
            #     }
            # }
            # headers = {
            # "Authorization": f"Bearer {access_token}",
            # "Content-Type": "application/json"
            # }
            # url = Config.FIREBASE_FCM_URL
            
            # async with httpx.AsyncClient() as client:
            #     response = await client.post(url, headers=headers, json=message)

            # # Check if the request was successful
            # if response.status_code == 200:
            #     return {"success": True, "message": "Notification sent successfully"}
            # else:
                # raise HTTPException(
                #     status_code=response.status_code,
                #     detail=f"Failed to send notification: {response.text}"
                # )
            return {"success": True, "message": "Notification sent successfully"}
        except Exception as e:
            print(f"Error sending notification: {e}")
            raise e
    
    def send_push_notifications(self, tokens: List[str], title: str, body: str, data: dict = None):
        # Initialize Firebase App only if not already initialized
        if not firebase_admin._apps:
            print('Init Firebase')
            cred = credentials.Certificate(Config.SERVICE_KEY_FILE)
            firebase_admin.initialize_app(cred)
            
        self.get_access_token()
        
        notification = messaging.Notification(
            title=title,
            body=body
        )
        
        message = messaging.MulticastMessage(
            notification=notification,
            tokens=tokens,
            data=data or {}
        )
        
        response = messaging.send_multicast(message)
        print(f'Successfully sent to {response.success_count} devices, failed to send to {response.failure_count} devices')
        
        # Print errors for each failed token
        for idx, resp in enumerate(response.responses):
            if not resp.success:
                print(f"Token {tokens[idx]} failed with error: {resp.exception}")
        

    
    