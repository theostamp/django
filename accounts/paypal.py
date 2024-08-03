import paypalrestsdk
import logging

paypalrestsdk.configure({
    "mode": "sandbox",  # ή "live" για παραγωγή
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET"
})

logging.basicConfig(level=logging.INFO)
