    def get_products(self):
        # Database mein 'products' node se saara data uthaye ga
        return db.reference('products').get()
        
