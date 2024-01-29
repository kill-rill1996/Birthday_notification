import os
from dotenv import load_dotenv

load_dotenv()
# telegram
TOKEN = os.getenv('TOKEN')

# db postgresql
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')
DB_HOST = os.getenv('POSTGRES_HOST')
DB_PORT = os.getenv('POSTGRES_PORT')

# callback query salt
SALT = os.getenv("SALT")