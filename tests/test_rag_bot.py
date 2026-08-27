import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rag_bot import chunk_markdown, has_topic_overlap, load_chunks  # noqa: E402


class RAGBotTests(unittest.TestCase):
    def test_loads_the_three_source_documents(self):
        data_dir = Path(__file__).resolve().parents[1] / "data"
        chunks = load_chunks(data_dir)
        self.assertGreaterEqual(len(chunks), 10)
        self.assertEqual(
            {chunk.document for chunk in chunks},
            {"01-getting-started", "02-pricing-and-plans", "03-troubleshooting"},
        )


    def test_chunks_keep_section_for_citations(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            source = Path(directory) / "guide.md"
            source.write_text("# Guide\nIntro text.\n\n## Limits\nFifty notebooks.", encoding="utf-8")
            chunks = chunk_markdown(source)
        self.assertEqual(chunks[1].citation, "guide — Limits")
        self.assertEqual(chunks[1].text, "Limits\nFifty notebooks.")


    def test_topic_overlap_guard(self):
        self.assertTrue(has_topic_overlap("What is the Pro plan price?", "The Pro plan costs $6 per month."))
        self.assertFalse(has_topic_overlap("Who founded NimbusNote?", "The Pro plan costs $6 per month."))


if __name__ == "__main__":
    unittest.main()
