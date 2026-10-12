#!/usr/bin/env python3
"""ЛР №1. Индексирование и булев информационный поиск.

Источник данных: result.jsonl из seminars/02-scraping.
Внешние библиотеки не требуются.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import time
from collections import defaultdict
from pathlib import Path
from typing import Iterable


TOKEN_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")


def tokenize(text: str, min_len: int = 2) -> list[str]:
    """Нижний регистр + выделение слов + фильтрация по длине."""
    return [
        token
        for token in TOKEN_RE.findall((text or "").lower())
        if len(token) >= min_len
    ]


def load_documents(path: Path) -> list[dict]:
    """Читает JSONL, созданный семинаром 02."""
    documents: list[dict] = []

    with path.open("r", encoding="utf-8") as f:
        for source_id, line in enumerate(f):
            line = line.strip()
            if not line:
                continue

            obj = json.loads(line)

            # Формат FileSink из seminars/02-scraping:
            # {"tries": 0, "result": {...}, "error": null}
            if "result" in obj:
                if obj.get("error") is not None or not obj.get("result"):
                    continue
                item = obj["result"]
            else:
                item = obj

            title = str(item.get("title", ""))
            description = str(item.get("description", ""))
            genre = str(item.get("genre", ""))

            documents.append(
                {
                    "source_id": source_id,
                    "title": title,
                    "description": description,
                    "genre": genre,
                    "price": item.get("price"),
                    "text": f"{title} {description} {genre}",
                }
            )

    return documents


def sample_documents(
    documents: list[dict],
    n: int,
    random_state: int,
) -> list[dict]:
    """Формирует воспроизводимую случайную выборку."""
    if n <= 0:
        return list(documents)

    if len(documents) < n:
        raise ValueError(
            f"В корпусе только {len(documents)} документов, а требуется N={n}. "
            "Для варианта с большим N соберите весь каталог, задав в "
            "seminars/02-scraping/main.py seed URL "
            "'https://books.toscrape.com/index.html'."
        )

    rng = random.Random(random_state)
    return rng.sample(documents, n)


def build_inverted_index(
    documents: list[dict],
    min_len: int,
) -> dict[str, set[int]]:
    """Строит индекс term -> множество локальных doc_id."""
    index: dict[str, set[int]] = defaultdict(set)

    for doc_id, document in enumerate(documents):
        # В posting list документ должен встречаться один раз.
        terms = set(tokenize(document["text"], min_len=min_len))
        for term in terms:
            index[term].add(doc_id)

    return dict(index)


def boolean_search(
    query: str,
    index: dict[str, set[int]],
    operator: str,
    min_len: int,
) -> tuple[list[str], list[int]]:
    """Выполняет AND/OR-поиск."""
    terms = tokenize(query, min_len=min_len)
    if not terms:
        return [], []

    postings = [index.get(term, set()) for term in terms]
    operator = operator.upper()

    if operator == "AND":
        result = set.intersection(*postings) if postings else set()
    elif operator == "OR":
        result = set.union(*postings) if postings else set()
    else:
        raise ValueError("operator должен быть AND или OR")

    return terms, sorted(result)


def save_index(index: dict[str, set[int]], path: Path) -> None:
    serializable = {term: sorted(ids) for term, ids in sorted(index.items())}
    path.write_text(
        json.dumps(serializable, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("data", type=Path, help="Путь к result.jsonl")
    parser.add_argument("--n", type=int, default=500, help="Размер выборки; 0 = весь корпус")
    parser.add_argument("--random-state", type=int, default=101)
    parser.add_argument("--min-len", type=int, default=2)
    parser.add_argument("--operator", choices=["AND", "OR"], default="AND")
    parser.add_argument("--query", default="magic world")
    parser.add_argument("--index-file", type=Path, default=Path("index.json"))
    parser.add_argument("--result-file", type=Path, default=Path("lab_01_results.json"))
    args = parser.parse_args()

    documents_all = load_documents(args.data)
    documents = sample_documents(documents_all, args.n, args.random_state)

    t0 = time.perf_counter()
    index = build_inverted_index(documents, args.min_len)
    build_time = time.perf_counter() - t0

    t1 = time.perf_counter()
    terms, found_ids = boolean_search(
        args.query,
        index,
        args.operator,
        args.min_len,
    )
    search_time = time.perf_counter() - t1

    save_index(index, args.index_file)

    found = [
        {
            "doc_id": doc_id,
            "source_id": documents[doc_id]["source_id"],
            "title": documents[doc_id]["title"],
            "genre": documents[doc_id]["genre"],
            "price": documents[doc_id]["price"],
        }
        for doc_id in found_ids
    ]

    report = {
        "corpus_total": len(documents_all),
        "sample_size": len(documents),
        "random_state": args.random_state,
        "min_len": args.min_len,
        "vocabulary_size": len(index),
        "build_time_seconds": build_time,
        "query": args.query,
        "query_terms": terms,
        "operator": args.operator,
        "results_count": len(found),
        "search_time_seconds": search_time,
        "results": found,
    }

    args.result_file.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Всего документов в корпусе : {len(documents_all)}")
    print(f"Документов в выборке       : {len(documents)}")
    print(f"Размер словаря             : {len(index)}")
    print(f"Построение индекса         : {build_time:.6f} с")
    print(f"Запрос                     : {args.query!r}")
    print(f"Оператор                   : {args.operator}")
    print(f"Токены запроса             : {terms}")
    print(f"Найдено документов         : {len(found)}")
    print(f"Время поиска               : {search_time:.8f} с")
    print()

    for row in found[:10]:
        print(f"[{row['doc_id']:>4}] {row['title']}")

    print(f"\nИндекс сохранен: {args.index_file}")
    print(f"Отчет сохранен : {args.result_file}")


if __name__ == "__main__":
    main()
