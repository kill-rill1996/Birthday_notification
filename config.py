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

# admins tg_ids
ADMINS = [int(admin) for admin in os.getenv('ADMINS').split(',')]

# notify in days before
DAYS_BEFORE = [int(day) for day in os.getenv("DAYS_BEFORE").split(',')]

# amounts for events kb
PAID1 = os.getenv("PAID1")
PAID2 = os.getenv("PAID2")
PAID3 = os.getenv("PAID3")

# admins phones for pay
PHONES = [phone for phone in os.getenv("PHONES").split(",")]

# days before admins pick phone number for bd pay
DAYS_BEFORE_PHONE = int(os.getenv("DAYS_BEFORE_PHONE"))
