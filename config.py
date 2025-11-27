import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')

# Validate required settings
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in .env file")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env file")