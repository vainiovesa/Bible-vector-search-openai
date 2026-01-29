import json


def _get_bible(file:str):
    with open(file, "r") as file:
        Bible = json.loads(file.read())
    return Bible


def base_verses_formatted(file:str):
    data = []
    Bible = _get_bible(file)
    for book in Bible:
        book_name = book["name"]
        chapters = book["chapters"]
        for chapter_num in range(len(chapters)):
            verses = chapters[chapter_num]
            for verse_num in range(len(verses)):
                data.append((book_name, chapter_num, verse_num))
    return data
