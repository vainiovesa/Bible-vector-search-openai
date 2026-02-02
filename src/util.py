from dotenv import load_dotenv
from openai import OpenAI
import numpy as np
import json


load_dotenv()


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


def verses_formatted(file:str, translation_id:int, verse_ids:list):
    data = []
    Bible = _get_bible(file)
    for book in Bible:
        chapters = book["chapters"]
        for chapter in chapters:
            embeddings = embed(chapter)
            data.extend(zip(chapter, embeddings))

    data = [(translation_id, verse_ids[i], text, np.array(embedding)) for i, (text, embedding) in enumerate(data)]
    return data


def embed(input):
    client = OpenAI()
    response = client.embeddings.create(input=input, model='text-embedding-3-small')
    return [v.embedding for v in response.data]
