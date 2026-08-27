"""A small, transparent retrieval-first Q&A bot for the NimbusNote docs."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_MODEL = "all-MiniLM-L6-v2"
MIN_RETRIEVAL_SCORE = 0.32
TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class Chunk:
    """One citeable document passage."""

    document: str
    section: str
    text: str

    @property
    def citation(self) -> str:
        return f"{self.document} — {self.section}"


@dataclass(frozen=True)
class SearchResult:
    chunk: Chunk
    score: float


def chunk_markdown(path: Path) -> list[Chunk]:
    """Split a Markdown document by headings, preserving meaningful passages."""
    title = path.stem
    section = "Introduction"
    parts: list[tuple[str, list[str]]] = []
    buffer: list[str] = []

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("#"):
            if buffer:
                parts.append((section, buffer))
            section = line.lstrip("#").strip()
            buffer = []
        elif line:
            buffer.append(line)
    if buffer:
        parts.append((section, buffer))

    # Include the heading in both the embedding and the displayed evidence: key
    # facts (for example, the Pro plan price) can live in a Markdown heading.
    return [Chunk(title, heading, f"{heading}\n" + " ".join(lines)) for heading, lines in parts]


def load_chunks(data_dir: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(data_dir.glob("*.md")):
        if path.name.lower() != "readme.md":
            chunks.extend(chunk_markdown(path))
    if not chunks:
        raise ValueError(f"No Markdown source documents found in {data_dir}")
    return chunks


class Retriever:
    """In-memory cosine-similarity vector store."""

    def __init__(self, chunks: list[Chunk], model_name: str = DEFAULT_MODEL):
        # Imports stay here so the document/chunking utilities and their tests do
        # not require downloading the embedding runtime.
        import numpy as np
        from sentence_transformers import SentenceTransformer

        self.chunks = chunks
        self.model = SentenceTransformer(model_name)
        # Normalizing means a dot product is cosine similarity.
        self.embeddings = self.model.encode(
            [chunk.text for chunk in chunks], normalize_embeddings=True, show_progress_bar=False
        )

    def search(self, question: str, top_k: int = 3) -> list[SearchResult]:
        import numpy as np

        question_embedding = self.model.encode(question, normalize_embeddings=True, show_progress_bar=False)
        scores = np.dot(self.embeddings, question_embedding)
        best_indices = np.argsort(scores)[::-1][:top_k]
        return [SearchResult(self.chunks[i], float(scores[i])) for i in best_indices]


def has_topic_overlap(question: str, passage: str) -> bool:
    """A small guard against returning a semantically nearby but unsupported answer."""
    stop_words = {"a", "an", "and", "are", "can", "do", "does", "for", "how", "i", "in", "is", "it", "me", "my", "nimbusnote", "of", "on", "or", "the", "to", "what", "when", "with", "you", "your"}
    query_words = set(TOKEN_RE.findall(question.lower())) - stop_words
    passage_words = set(TOKEN_RE.findall(passage.lower()))
    return bool(query_words & passage_words)


def answer_question(retriever: Retriever, question: str, top_k: int = 3) -> str:
    """Return only retrieved evidence, or explicitly decline when evidence is weak."""
    results = retriever.search(question, top_k=top_k)
    best = results[0]
    if best.score < MIN_RETRIEVAL_SCORE or not has_topic_overlap(question, best.chunk.text):
        return (
            "I couldn't find an answer to that in the supplied NimbusNote documents. "
            "Try asking about workspaces, notes, sync, plans, billing, or troubleshooting."
        )

    # This is deliberately extractive: no LLM is allowed to invent details beyond the source.
    evidence = [result for result in results if result.score >= MIN_RETRIEVAL_SCORE]
    rendered_sources = "\n\n".join(
        f"[{item.chunk.citation}] (similarity: {item.score:.2f})\n{item.chunk.text}"
        for item in evidence
    )
    return f"Based on the retrieved documentation:\n\n{rendered_sources}"


def ask_loop(retriever: Retriever, question: str | None, top_k: int) -> None:
    if question:
        print(answer_question(retriever, question, top_k))
        return
    print("NimbusNote RAG bot. Type a question, or 'quit' to exit.")
    while True:
        try:
            user_question = input("\nQuestion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if user_question.lower() in {"quit", "exit", "q"}:
            break
        if user_question:
            print("\n" + answer_question(retriever, user_question, top_k))


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Retrieval-first Q&A over the NimbusNote docs")
    parser.add_argument("--question", "-q", help="Ask one question and exit")
    parser.add_argument("--data-dir", type=Path, default=project_root / "data")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Sentence-Transformers model name")
    args = parser.parse_args()
    if args.top_k < 1:
        parser.error("--top-k must be at least 1")
    retriever = Retriever(load_chunks(args.data_dir), args.model)
    ask_loop(retriever, args.question, args.top_k)


if __name__ == "__main__":
    main()
