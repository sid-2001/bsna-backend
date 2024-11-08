import firebase_admin
from firebase_admin import credentials, messaging
from typing import List, Optional
from src.config import Config

class FirebaseConfig():
    
    def send_push_notifications(self,tokens:list[str], title:str, body:str, data:dict = None):
        cred = credentials.Certificate(Config.SERVICE_KEY_FILE)
        firebase_admin.initialize_app(cred)
        
        # message = messaging.MulticastMessage(
        #     notification=messaging.Notification(
        #         title=title,
        #         body=body
        #     ),
        #     tokens=tokens,
        #     data=data
        # )
        
        notification = messaging.Notification(
            title=title,
            body=body
        )
        
        message = messaging.MulticastMessage(
            notification=notification,
            tokens=tokens
        )
        
        response = messaging.send_multicast(message)
        print(f'Successfully sent to {response.success_count} devices, failed to send to {response.failure_count} devices')
        

    
    