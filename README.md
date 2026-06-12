# Joropixal Bot 🤖

Telegram bot for selling digital products with Firebase backend.

## Project Structure
```
Joropixal/
├── main.py
├── FirebaseService.py
├── requirements.txt
├── .gitignore
└── bot/
    ├── __init__.py
    └── handlers/
        ├── __init__.py
        ├── user.py
        └── admin.py
```

## Render Environment Variables

Set these in Render Dashboard → Environment:

| Key | Value |
|-----|-------|
| `BOT_TOKEN` | Your Telegram Bot Token |
| `FIREBASE_JSON` | Full content of serviceAccountKey.json |
| `ADMIN_IDS` | Your Telegram User ID (e.g. `123456789`) |
| `PORT` | `10000` |

## Render Settings
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python3 main.py`
- **Instance Type:** Free

## Features
- 🛍️ Product listing with QR payment
- 💰 Payment notification to admin
- ✅ Admin approve/reject orders
- 📦 User purchase history
- ⚙️ Admin panel (add/delete products, view users)
