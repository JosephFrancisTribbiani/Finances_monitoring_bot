from os import environ
from dotenv import load_dotenv

# Загрузка значений переменных окружения
load_dotenv()


TOKEN = '1474084336:AAEAU5UFYEBctyhkmVWNW5N9QTS8sN8IAtE'
# DATABASE_URL = 'postgres://bvzqiaqdotxmbs:46f133b16a9f69bb5fd3ee6e0bdbbe9b0dba86f9049ffecf17a0e58610849dea@ec2-46-137-124-19.eu-west-1.compute.amazonaws.com:5432/d8hjk48q7mt2id'
DATABASE_URL = environ.get('DATABASE_URL')
