import db
from util import query_embedding_formatted


def search(query:str, limit:int):
    sql = """
        SELECT
            tr.version,
            v.book,
            v.chapter + 1,
            v.verse + 1,
            trv.content,
            trv.embedding <=> %s AS distance
        FROM
            translations_verses trv, translations tr, verses v
        WHERE
            trv.translation_id = tr.id AND
            trv.verse_id = v.id
        ORDER BY distance
        LIMIT %s
    """
    embedding = query_embedding_formatted(query)
    params = [embedding, limit]
    result = db.query(sql, params)
    return result
