import firebase_admin
from firebase_admin import credentials, db

# Ye file aapke root folder mein मौजूद hai
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://joro-gaming-default-rtdb.firebaseio.com' 
})

# Ab hum DB ka reference le rahe hain
class FirebaseService:
    def get_order(self, order_id):
        # Yeh function orders table se data fetch karega
        return db.reference(f'orders/{order_id}').get()

    def update_order(self, order_id, data):
        # Yeh function status update karega
        db.reference(f'orders/{order_id}').update(data)
        