from os import environ
from dotenv import load_dotenv

# загружаем переменные окружения

load_dotenv()

TOKEN = environ.get('TOKEN')
DATABASE_URL = environ.get('DATABASE_URL')
