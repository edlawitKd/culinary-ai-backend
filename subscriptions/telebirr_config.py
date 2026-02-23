import hashlib
import hmac
import json
import base64
import requests
from django.conf import settings

class TelebirrConfig:
    # Get these from your Telebirr merchant account
    APP_ID = settings.TELEBIRR_APP_ID  # Add to settings.py
    APP_KEY = settings.TELEBIRR_APP_KEY  # Add to settings.py
    PUBLIC_KEY = settings.TELEBIRR_PUBLIC_KEY  # Add to settings.py
    MERCHANT_CODE = settings.TELEBIRR_MERCHANT_CODE  # Add to settings.py
    
    # Telebirr API endpoints
    BASE_URL = "https://api.telebirr.com"  # Production URL
    # BASE_URL = "https://test-api.telebirr.com"  # Test URL
    
    PAYMENT_URL = f"{BASE_URL}/payment/create"
    QUERY_URL = f"{BASE_URL}/payment/query"
    
    # Return URLs
    RETURN_URL = settings.TELEBIRR_RETURN_URL  # Where user returns after payment
    NOTIFY_URL = settings.TELEBIRR_NOTIFY_URL  # Your callback URL