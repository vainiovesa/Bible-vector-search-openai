import os
import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector


load_dotenv()

DB_NAME = os.environ.get("DB_NAME")
PG_USER = os.environ.get("POSTGRES_USER")
PG_PASSWORD = os.environ.get("POSTGRES_PASSWORD")


def get_connection():
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


def reinitialize():
    conn = get_connection()

    sql = "DROP TABLE IF EXISTS translations_verses"
    conn.execute(sql)
    sql = "DROP TABLE IF EXISTS translations"
    conn.execute(sql)
    sql = "DROP TABLE IF EXISTS verses"
    conn.execute(sql)

    sql = """CREATE TABLE translations (
        id      SERIAL PRIMARY KEY,
        version TEXT NOT NULL UNIQUE
    )"""
    conn.execute(sql)

    sql = """CREATE TABLE verses (
        id          SERIAL PRIMARY KEY,
        book        TEXT NOT NULL,
        chapter     INTEGER NOT NULL,
        verse       INTEGER NOT NULL,
        UNIQUE (book, chapter, verse)
    )"""
    conn.execute(sql)

    sql = """CREATE TABLE translations_verses (
        translation_id  INTEGER NOT NULL,
        verse_id        INTEGER NOT NULL,
        content         TEXT NOT NULL,
        embedding       VECTOR(1536) NOT NULL,
        PRIMARY KEY (translation_id, verse_id),
        FOREIGN KEY (translation_id) REFERENCES translations(id) ON DELETE CASCADE,
        FOREIGN KEY (verse_id) REFERENCES verses(id) ON DELETE CASCADE
    )"""
    conn.execute(sql)

    sql = "CREATE INDEX idx_translations_verses_translation ON translations_verses (translation_id)"
    conn.execute(sql)

    sql = "CREATE INDEX idx_translations_verses_verse ON translations_verses (verse_id)"
    conn.execute(sql)

    sql = """CREATE INDEX idx_translations_verses_embedding
        ON translations_verses
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 300)
    """
    conn.execute(sql)
    conn.close()
