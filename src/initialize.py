import db
from util import base_verses_formatted


TRANSLATION = "Biblia"
DATA_FILE = "fi1776_bible.json"


def reinitialize():
    sqls = []

    sqls.append("DROP TABLE IF EXISTS translations_verses")
    sqls.append("DROP TABLE IF EXISTS translations")
    sqls.append("DROP TABLE IF EXISTS verses")

    sqls.append("""CREATE TABLE translations (
        id      SERIAL PRIMARY KEY,
        version TEXT NOT NULL UNIQUE
    )""")
    sqls.append("""CREATE TABLE verses (
        id          SERIAL PRIMARY KEY,
        book        TEXT NOT NULL,
        chapter     INTEGER NOT NULL,
        verse       INTEGER NOT NULL,
        UNIQUE (book, chapter, verse)
    )""")
    sqls.append("""CREATE TABLE translations_verses (
        translation_id  INTEGER NOT NULL,
        verse_id        INTEGER NOT NULL,
        content         TEXT NOT NULL,
        embedding       VECTOR(1536) NOT NULL,
        PRIMARY KEY (translation_id, verse_id),
        FOREIGN KEY (translation_id) REFERENCES translations(id) ON DELETE CASCADE,
        FOREIGN KEY (verse_id) REFERENCES verses(id) ON DELETE CASCADE
    )""")

    for sql in sqls:
        db.execute(sql)


def create_indexes():
    sqls = []
    sqls.append("""CREATE INDEX idx_translations_verses_translation
        ON translations_verses (translation_id)""")
    sqls.append("""CREATE INDEX idx_translations_verses_verse
        ON translations_verses (verse_id)""")
    sqls.append("""CREATE INDEX idx_translations_verses_embedding
        ON translations_verses
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 300)
    """)

    for sql in sqls:
        db.execute(sql)


def add_translation(name):
    sql = "INSERT INTO translations (version) VALUES (%s) RETURNING id"
    translation_id = db.execute(sql, [name])
    return translation_id


def add_base_verses(from_file:str):
    data = base_verses_formatted(from_file)
    verse_ids = []
    sql = "INSERT INTO verses (book, chapter, verse) VALUES (%s, %s, %s) RETURNING id"
    for row in data:
        verse_id = db.execute(sql, row)
        verse_ids.append(verse_id)
    return verse_ids
