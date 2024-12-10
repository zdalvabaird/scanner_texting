import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration class
class Config:
    # Test mode flag
    TEST_MODE = os.getenv('TEST_MODE', 'True').lower() == 'true'
    
    # Twilio credentials (will be None in test mode)
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

    # Database settings
    DATABASE_NAME = 'mappings.db'