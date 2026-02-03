import db
from util import base_verses_formatted, verses_formatted


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
    translation_id = db.execute_returning(sql, [name])
    return translation_id


def add_base_verses(from_file:str):
    print("[BASE VERSE ADD] Started")
    data = base_verses_formatted(from_file)
    verse_ids = []
    sql = "INSERT INTO verses (book, chapter, verse) VALUES (%s, %s, %s) RETURNING id"
    n = len(data)
    m = n // 100
    print("[BASE VERSE ADD] Started inserting verses")
    for i, row in enumerate(data):
        verse_id = db.execute_returning(sql, row)
        verse_ids.append(verse_id)

        if i % m == 0:
            print('.', end='', flush=True)
    print("[BASE VERSE ADD] Ready")
    return verse_ids


def add_verses(from_file:str, translation_id:int, verse_ids:list):
    print("[VERSE ADD] Started")
    data = verses_formatted(from_file, translation_id, verse_ids)
    sql = "COPY translations_verses (translation_id, verse_id, content, embedding) FROM STDIN WITH (FORMAT BINARY)"
    types = ["integer", "integer", "text", "vector"]
    print("[VERSE ADD] Bulk save started")
    db.bulk_save(sql, types, data)
    print("[VERSE ADD] Ready")


def full_reinitialization():
    print("[FULL REINIT] Started")
    print("[FULL REINIT] Started clearing tables")
    reinitialize()
    print("[FULL REINIT] Tables cleared")
    print("[FULL REINIT] Adding translation")
    translation_id = add_translation(TRANSLATION)
    print("[FULL REINIT] Translation added")
    print("[FULL REINIT] Started adding base verses")
    verse_ids = add_base_verses(DATA_FILE)
    print("[FULL REINIT] Base verses added")
    print("[FULL REINIT] Started adding verses")
    add_verses(DATA_FILE, translation_id, verse_ids)
    print("[FULL REINIT] Verses added")
    print("[FULL REINIT] Ready")

if __name__ == "__main__":
    full_reinitialization()
