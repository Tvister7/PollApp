import os
from dotenv import load_dotenv
from contextlib import contextmanager
from psycopg2.pool import SimpleConnectionPool

DATABASE_PROMPT = "Введите свой DATABASE_URI или оставьте поле пустым, чтобы загрузить его из .env: "

database_uri = input(DATABASE_PROMPT)
if not database_uri:
    load_dotenv()
    database_uri = os.environ.get("DATABASE_URI")

pool = SimpleConnectionPool(minconn=1, maxconn=10, dsn=database_uri)


@contextmanager
def get_cursor(connection):
    with connection:
        with connection.cursor() as cursor:
            yield cursor


@contextmanager
def get_connection():
    connection = pool.getconn()

    try:
        yield connection
    finally:
        pool.putconn(connection)
