import os
import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector


load_dotenv()

DB_NAME = os.environ.get("DB_NAME")
PG_USER = os.environ.get("POSTGRES_USER")
PG_PASSWORD = os.environ.get("POSTGRES_PASSWORD")


def _get_connection():
    conn = psycopg.connect(
        host="localhost",
        port=5432,
        dbname=DB_NAME,
        user=PG_USER,
        password=PG_PASSWORD,
        autocommit=True
    )

    sql = "CREATE EXTENSION IF NOT EXISTS vector"
    conn.execute(sql)
    register_vector(conn)

    return conn


def execute(sql:str, params:list=[]):
    conn = _get_connection()
    conn.execute(sql, params)
    conn.close()


def query(sql:str, params:list=[]):
    conn = _get_connection()
    result = conn.execute(sql, params).fetchall()
    conn.close()
    return result
