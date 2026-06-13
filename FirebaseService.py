import os
import json
import firebase_admin
from firebase_admin import credentials, db

if os.path.exists("serviceAccountKey.json"):
    cred = credentials.Certificate("serviceAccountKey.json")
else:
    cred = credentials.Certificate(json.loads(os.getenv("FIREBASE_JSON")))

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://new-bot-projext-default-rtdb.firebaseio.com'
})

class FirebaseService:

    def get_all_products(self):
        data = db.reference('products').get()
        if not data:
            return []
        return [{'id': k, **v} for k, v in data.items()]

    def add_product(self, name, price, description, qr_url):
        ref = db.reference('products').push({
            'name': name, 'price': price,
            'description': description, 'qr_url': qr_url, 'active': True
        })
        return ref.key

    def update_product(self, product_id, data):
        db.reference(f'products/{product_id}').update(data)

    def delete_product(self, product_id):
        db.reference(f'products/{product_id}').delete()

    def get_product(self, product_id):
        return db.reference(f'products/{product_id}').get()

    def create_order(self, user_id, username, product_id, product_name, price):
        ref = db.reference('orders').push({
            'user_id': user_id, 'username': username,
            'product_id': product_id, 'product_name': product_name,
            'price': price, 'status': 'pending'
        })
        return ref.key

    def get_order(self, order_id):
        return db.reference(f'orders/{order_id}').get()

    def update_order(self, order_id, data):
        db.reference(f'orders/{order_id}').update(data)

    def get_pending_orders(self):
        data = db.reference('orders').get()
        if not data:
            return []
        return [{'id': k, **v} for k, v in data.items() if v.get('status') == 'pending']

    def get_user_orders(self, user_id):
        data = db.reference('orders').get()
        if not data:
            return []
        return [{'id': k, **v} for k, v in data.items()
                if str(v.get('user_id')) == str(user_id) and v.get('status') == 'approved']

    def save_user(self, user_id, username, full_name):
        db.reference(f'users/{user_id}').set({
            'username': username, 'full_name': full_name, 'user_id': user_id
        })

    def get_all_users(self):
        data = db.reference('users').get()
        if not data:
            return []
        return [{'id': k, **v} for k, v in data.items()]
                  
