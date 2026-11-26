import re

import pytest

from niu_assistant import evaluate, index

QUESTIONS = evaluate.load()


def test_every_source_is_pinned():
    for page in index.pages().values():
        assert re.fullmatch(r"[0-9a-f]{40}|v\d+(\.\d+)*", page["ref"])


def test_every_question_names_an_indexed_page():
    assert len(QUESTIONS) == 10
    for question in QUESTIONS:
        assert question["page"] in index.pages()


@pytest.mark.parametrize("question", QUESTIONS, ids=lambda q: q["id"])
def test_question_finds_its_page_in_top_three(question):
    hits = [hit["id"] for hit in index.find_docs(question["question"])]
    assert question["page"] in hits[:3]
