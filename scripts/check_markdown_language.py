"""Reject substantial Portuguese prose in repository Markdown files.

This lightweight heuristic complements human review; short phrases and quoted
examples may require manual inspection. The bilingual product UI lives in
locale resources, not Markdown documentation.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


PORTUGUESE = {
    "não", "para", "com", "que", "uma", "como", "também", "está", "será",
    "dos", "das", "pelo", "pela", "sobre", "aqui", "quando", "isso", "são",
    "seu", "sua", "esse", "essa", "este", "esta", "mais", "menos", "até",
    "após", "antes", "pode", "podem", "entre", "deve", "devem", "onde",
    "cada", "sem", "aos", "nas", "nos", "porque", "então", "fazer", "precisa",
    "usuário", "usuários", "campo", "chute", "jogadores", "goleiro",
    "defensores", "explicação", "estimativa", "modelo", "dados",
}
ENGLISH = {
    "the", "and", "with", "for", "from", "that", "this", "these", "those",
    "when", "where", "which", "what", "will", "would", "should", "must",
    "can", "could", "into", "without", "before", "after", "about", "between",
    "each", "every", "their", "there", "then", "than", "because", "also",
    "using", "user", "users", "field", "shot", "players", "goalkeeper",
    "defenders", "explanation", "estimate", "model", "data",
}
WORD = re.compile(r"[^\W\d_]+", re.UNICODE)
FENCE = re.compile(r"^\s*(```|~~~)")
URL = re.compile(r"https?://\S+")
INLINE_CODE = re.compile(r"`[^`]*`")


def prose_paragraphs(content: str):
    chunks: list[str] = []
    fenced = False
    for line in content.splitlines():
        if FENCE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        line = URL.sub("", INLINE_CODE.sub("", line))
        if not line.strip():
            if chunks:
                yield " ".join(chunks)
                chunks.clear()
        else:
            chunks.append(line)
    if chunks:
        yield " ".join(chunks)


def portuguese_prose(paragraph: str) -> bool:
    words = [word.casefold() for word in WORD.findall(paragraph)]
    if len(words) < 8:
        return False
    pt = sum(word in PORTUGUESE for word in words)
    en = sum(word in ENGLISH for word in words)
    return pt >= 4 and pt > en * 1.2 and len(set(words) & PORTUGUESE) >= 3


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    failures = []
    for path in root.rglob("*.md"):
        if any(part in {".git", "node_modules", ".next"} for part in path.parts):
            continue
        for number, paragraph in enumerate(prose_paragraphs(path.read_text(encoding="utf-8")), 1):
            if portuguese_prose(paragraph):
                failures.append(f"{path.relative_to(root)}: paragraph {number}")
    if failures:
        print("Markdown prose must be in English. Possible Portuguese content:")
        print("\n".join(failures))
        return 1
    print("Markdown language check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
