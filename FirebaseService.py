import json
import os
from firebase_admin import credentials

# Environment variable se json uthayein
json_data = json.loads(os.getenv("FIREBASE_JSON"))
cred = credentials.Certificate(json_data)
