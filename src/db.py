import os
import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector


load_dotenv()

DB_NAME = os.environ.get("DB_NAME")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
PG_USER = os.environ.get("POSTGRES_USER")
PG_PASSWORD = os.environ.get("POSTGRES_PASSWORD")


def _get_connection():
    conn = psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
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


def execute_returning(sql:str, params:list=[]):
    conn = _get_connection()
    result = conn.execute(sql, params)
    to_return = result.fetchone()
    conn.close()
    return to_return[0] if to_return else None


def query(sql:str, params:list=[]):
    conn = _get_connection()
    result = conn.execute(sql, params).fetchall()
    conn.close()
    return result


def bulk_save(sql:str, types:list, data:list):
    conn = _get_connection()
    cur = conn.cursor()
    m = len(data) // 100
    m = 1 if m == 0 else m
    with cur.copy(sql) as copy:
        copy.set_types(types)
        for i, row in enumerate(data):
            copy.write_row(row)

            if i % m == 0:
                print('.', end='', flush=True)
