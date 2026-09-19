# NimbusNote RAG Mini Q&A Bot

A compact, retrieval-first question-answering bot over the supplied NimbusNote documentation. It uses a free local `sentence-transformers` embedding model and an in-memory cosine-similarity vector store—no hosted API key is needed.

## What it demonstrates

1. Loads the supplied Markdown documents from `data/`.
2. Chunks them by heading so each result is a meaningful, citeable passage.
3. Embeds every passage with `all-MiniLM-L6-v2` (downloaded automatically on the first run).
4. Embeds the question, ranks passages with cosine similarity, and displays the retrieved evidence and source citations.
5. Refuses to answer when retrieval confidence or topic overlap is too weak, instead of inventing an answer.

The response is deliberately **extractive**: it shows the actual retrieved text rather than asking an LLM to generate an unsupported answer. This makes the grounding visible and easy to evaluate.

## Project structure

```
rag-qa-bot/
├── data/                 # supplied NimbusNote source documents
├── src/rag_bot.py        # chunking, embedding, retrieval, CLI
├── tests/test_rag_bot.py # lightweight unit tests
├── requirements.txt
└── README.md
```


The first query downloads the small free `all-MiniLM-L6-v2` model. Later runs use the local cache.

## Run It

Ask one question:

```bash
python3 src/rag_bot.py --question "How often does NimbusNote sync in the background?"
```

Or start an interactive session:

```bash
python3 src/rag_bot.py
```

Useful demo questions:

```text
How much does the Pro plan cost?
What should I do when I see two versions of a note?
How long do password reset emails last?
Who founded NimbusNote?   # expected: not found in the supplied docs
```

Each grounded response prints the document filename, its heading, similarity score, and the exact retrieved passage. The final example demonstrates the not-found guard.

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Retrieval pipeline

```
Markdown documents → heading-based chunks → local embeddings → in-memory vectors
question → local embedding → cosine similarity ranking → confidence/topic guard → cited evidence or not-found
```

`MIN_RETRIEVAL_SCORE` is set to `0.32` in `src/rag_bot.py`. The lexical topic-overlap check is an additional safety net: it reduces the chance that a merely similar passage is presented as evidence for an unrelated question.

## Source documents

The `data/` directory is a copy of the task corpus from [MLSA-SRM/recruit-task-rag-docs](https://github.com/MLSA-SRM/recruit-task-rag-docs). NimbusNote is fictional and the bot intentionally answers only from this corpus.

