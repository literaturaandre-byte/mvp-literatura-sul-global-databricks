import json
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

OPENLIBRARY_BASE_URL = "https://openlibrary.org"
REQUEST_DELAY_SECONDS = 1

OPENLIBRARY_AUTHOR_IDS = [
    "OL1527013A",
    "OL12217460A",
    "OL6495716A",
    "OL5697446A",
    "OL8701565A",
    "OL5122048A",
    "OL2940871A",
    "OL7633883A",
    "OL9081057A",
    "OL13513413A",
    "OL11730977A",
    "OL10432462A",
    "OL5533173A",
    "OL718270A",
]


def fetch_json(url: str) -> dict:
    request = Request(
        url,
        headers={
            "User-Agent": "mvp-literatura-sul-global-databricks/1.0 (academic data pipeline)"
        },
    )

    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def extract_author_profile(author_id: str) -> dict:
    url = f"{OPENLIBRARY_BASE_URL}/authors/{author_id}.json"
    return {
        "source_url": url,
        "extracted_at_utc": datetime.now(timezone.utc).isoformat(),
        "data": fetch_json(url),
    }


def extract_author_works(author_id: str) -> dict:
    url = f"{OPENLIBRARY_BASE_URL}/authors/{author_id}/works.json?limit=100"
    return {
        "source_url": url,
        "extracted_at_utc": datetime.now(timezone.utc).isoformat(),
        "data": fetch_json(url),
    }


def extract_all_authors() -> dict:
    extraction = {}

    for author_id in OPENLIBRARY_AUTHOR_IDS:
        extraction[author_id] = {
            "author_profile": extract_author_profile(author_id),
            "author_works": extract_author_works(author_id),
        }
        time.sleep(REQUEST_DELAY_SECONDS)

    return extraction


if __name__ == "__main__":
    result = extract_all_authors()
    print(json.dumps(result, ensure_ascii=False, indent=2))