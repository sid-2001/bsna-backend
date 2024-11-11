import firebase_admin
from firebase_admin import credentials, messaging
from typing import List, Optional
from src.config import Config

class FirebaseConfig():
    
    def send_push_notifications(self, tokens: List[str], title: str, body: str, data: dict = None):
        # Initialize Firebase App only if not already initialized
        if not firebase_admin._apps:
            print('Init Firebase')
            cred = credentials.Certificate(Config.SERVICE_KEY_FILE)
            firebase_admin.initialize_app(cred)
        
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
        

    
    