import db


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
