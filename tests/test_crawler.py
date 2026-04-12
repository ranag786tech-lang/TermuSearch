import unittest

from bs4 import BeautifulSoup

from crawler import build_keywords, extract_description, normalize_title


class CrawlerHelpersTests(unittest.TestCase):
    def test_normalize_title_uses_title(self):
        soup = BeautifulSoup("<html><title>  DigiD   Search </title></html>", "html.parser")
        self.assertEqual(normalize_title(soup, "https://example.com"), "DigiD Search")

    def test_extract_description_falls_back_to_og(self):
        soup = BeautifulSoup(
            '<html><meta property="og:description" content="Open graph description"></html>',
            "html.parser",
        )
        self.assertEqual(extract_description(soup), "Open graph description")

    def test_build_keywords_filters_short_tokens(self):
        keywords = build_keywords("AI for Search", "A fast search engine with modern UI")
        self.assertIn("search", keywords)
        self.assertNotIn("for", keywords)


if __name__ == "__main__":
    unittest.main()
