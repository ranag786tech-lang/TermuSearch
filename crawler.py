import argparse
import json
import os
from dataclasses import dataclass
from typing import Iterable, List

import requests
from bs4 import BeautifulSoup

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure
except Exception:  # pragma: no cover - handled gracefully at runtime
    MongoClient = None
    ConnectionFailure = Exception

DEFAULT_WEBSITES = [
    {"url": "https://en.wikipedia.org/wiki/Artificial_intelligence", "category": "All"},
    {"url": "https://en.wikipedia.org/wiki/Machine_learning", "category": "All"},
    {"url": "https://news.ycombinator.com", "category": "News"},
    {"url": "https://www.bbc.com/news", "category": "News"},
    {"url": "https://books.google.com", "category": "Books"},
    {"url": "https://www.goodreads.com", "category": "Books"},
    {"url": "https://finance.yahoo.com", "category": "Finance"},
    {"url": "https://www.bloomberg.com", "category": "Finance"},
    {"url": "https://unsplash.com", "category": "Images"},
    {"url": "https://www.pexels.com", "category": "Images"},
    {"url": "https://github.com", "category": "All"},
    {"url": "https://openai.com", "category": "All"},
    {"url": "https://www.youtube.com", "category": "Videos"},
    {"url": "https://vimeo.com", "category": "Videos"},
]


@dataclass
class CrawlResult:
    title: str
    link: str
    description: str
    category: str
    keywords: List[str]
    content: str


def normalize_title(soup: BeautifulSoup, url: str) -> str:
    if soup.title and soup.title.string:
        return " ".join(soup.title.string.split())[:200]
    return url


def extract_description(soup: BeautifulSoup) -> str:
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        return " ".join(meta_desc.get("content").split())[:500]

    og_desc = soup.find("meta", attrs={"property": "og:description"})
    if og_desc and og_desc.get("content"):
        return " ".join(og_desc.get("content").split())[:500]

    text = soup.get_text(separator=" ", strip=True)
    return text[:220]


def build_keywords(title: str, description: str) -> List[str]:
    tokens = set()
    for chunk in f"{title} {description}".lower().replace("/", " ").replace("-", " ").split():
        cleaned = "".join(ch for ch in chunk if ch.isalnum())
        if len(cleaned) >= 4:
            tokens.add(cleaned)
    return sorted(tokens)[:10]


def crawl_site(url: str, category: str, timeout: int) -> CrawlResult:
    response = requests.get(
        url,
        timeout=timeout,
        headers={"User-Agent": "Mozilla/5.0 (DigiD Crawler/2.0)"},
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    title = normalize_title(soup, url)
    description = extract_description(soup)
    content = soup.get_text(separator=" ", strip=True)[:1200]
    keywords = build_keywords(title, description)

    return CrawlResult(
        title=title,
        link=url,
        description=description,
        category=category,
        keywords=keywords,
        content=content,
    )


def write_data_js(results: Iterable[CrawlResult], output_path: str) -> None:
    payload = [
        {
            "title": row.title,
            "link": row.link,
            "description": row.description,
            "category": row.category,
            "keywords": row.keywords,
        }
        for row in results
    ]
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("const data = ")
        json.dump(payload, f, ensure_ascii=False, indent=4)
        f.write(";\n")


def save_to_mongo(results: Iterable[CrawlResult], mongo_uri: str, db_name: str, collection_name: str) -> None:
    if MongoClient is None:
        raise RuntimeError("pymongo is not installed. Run: pip install -r requirements.txt")

    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
        collection = client[db_name][collection_name]
        for row in results:
            collection.update_one(
                {"url": row.link},
                {
                    "$set": {
                        "title": row.title,
                        "description": row.description,
                        "content": row.content,
                        "url": row.link,
                        "category": row.category,
                        "keywords": row.keywords,
                        "status": "active",
                    }
                },
                upsert=True,
            )
    finally:
        client.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DigiD crawler with MongoDB + data.js fallback")
    parser.add_argument("--timeout", type=int, default=15, help="HTTP timeout in seconds")
    parser.add_argument("--output", default="data.js", help="Output path for generated data.js")
    parser.add_argument("--mongo-uri", default=os.getenv("MONGO_URI") or os.getenv("MONGODB_URI"))
    parser.add_argument("--mongo-db", default="DigiD_Search")
    parser.add_argument("--mongo-collection", default="web_index")
    parser.add_argument(
        "--mongo-only",
        action="store_true",
        help="Fail if MongoDB is unavailable instead of writing data.js only",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    print("=" * 50)
    print("🤖 DigiD Crawler Starting...")
    print("=" * 50)

    successful: List[CrawlResult] = []
    failed = 0

    for site in DEFAULT_WEBSITES:
        url = site["url"]
        category = site["category"]
        print(f"🕷️ Crawling: {url}")
        try:
            result = crawl_site(url, category, timeout=args.timeout)
            successful.append(result)
            print(f"   ✅ Saved: {result.title[:60]}")
        except requests.RequestException as exc:
            print(f"   ❌ Crawl error: {exc.__class__.__name__}")
            failed += 1

    if not successful:
        if args.mongo_only:
            print("❌ No pages were crawled successfully.")
            return 1
        print("⚠️ No pages were crawled successfully. Writing fallback index entries.")
        for site in DEFAULT_WEBSITES:
            successful.append(
                CrawlResult(
                    title=site["url"].replace("https://", "").replace("www.", "").split("/")[0],
                    link=site["url"],
                    description=f"Fallback entry for {site['url']} (crawl unavailable).",
                    category=site["category"],
                    keywords=[site["category"].lower(), "fallback", "digid", "search"],
                    content="",
                )
            )

    write_data_js(successful, args.output)
    print(f"✅ Wrote {len(successful)} records to {args.output}")

    if args.mongo_uri:
        try:
            save_to_mongo(successful, args.mongo_uri, args.mongo_db, args.mongo_collection)
            print("✅ MongoDB sync complete")
        except (ConnectionFailure, RuntimeError, Exception) as exc:
            if args.mongo_only:
                print(f"❌ MongoDB sync failed: {exc}")
                return 1
            print(f"⚠️ MongoDB sync skipped: {exc}")
    else:
        if args.mongo_only:
            print("❌ --mongo-only enabled, but MONGO_URI/MONGODB_URI is missing")
            return 1
        print("⚠️ MONGO_URI not found. Generated data.js only.")

    print("=" * 50)
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {failed}")
    print("🎉 DigiD Crawler finished!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
