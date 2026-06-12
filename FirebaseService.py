import firebase_admin
from firebase_admin import credentials, db

# serviceAccountKey.json aapke folder mein hona chahiye
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://joro-gaming-default-rtdb.firebaseio.com' 
})

class FirebaseService:
    def get_order(self, order_id):
        return db.reference(f'orders/{order_id}').get()

    def update_order(self, order_id, data):
        db.reference(f'orders/{order_id}').update(data)
        
    def get_products(self):
        # Yeh function products list karega
        return db.reference('products').get()
        
