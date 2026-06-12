import json
import os
import firebase_admin
from firebase_admin import credentials, db

# JSON load karna
json_data = json.loads(os.getenv("FIREBASE_JSON"))
cred = credentials.Certificate(json_data)
firebase_admin.initialize_app(cred, {'databaseURL': 'https://joro-gaming-default-rtdb.firebaseio.com'})

class FirebaseService:
    def update_order(self, order_id, data):
        db.reference(f'orders/{order_id}').update(data)
        
