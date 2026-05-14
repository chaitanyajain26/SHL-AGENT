from __future__ import annotations

import json
import time
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.config import get_settings
from app.models.catalog_models import CatalogItem
from app.scraper.parser import parse_assessment_page, parse_catalog_listing
from app.utils.logger import get_logger

logger = get_logger(__name__)


def session_with_retries() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=0.8,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({"User-Agent": "Mozilla/5.0 SHLAssessmentRecommender/1.0"})
    return session


def fetch(session: requests.Session, url: str, timeout: int) -> str:
    response = session.get(url, timeout=timeout)
    response.raise_for_status()
    return response.text


def scrape_catalog(output_path: Path | None = None) -> list[CatalogItem]:
    settings = get_settings()
    output = output_path or settings.catalog_path
    session = session_with_retries()
    logger.info("Scraping SHL catalog from %s", settings.catalog_url)
    listing_html = fetch(session, settings.catalog_url, settings.request_timeout_seconds)
    listing_rows = parse_catalog_listing(listing_html, settings.catalog_url)
    if not listing_rows:
        raise RuntimeError("No product catalog links were found on the SHL catalog page.")

    items_by_url: dict[str, CatalogItem] = {}
    for row in listing_rows:
        try:
            html = fetch(session, row["url"], settings.request_timeout_seconds)
            item = parse_assessment_page(row["name"], row["url"], html, row.get("summary", ""))
            if "packaged job solution" not in item.description.lower():
                items_by_url[str(item.url)] = item
            time.sleep(0.15)
        except Exception as exc:
            logger.warning("Skipping %s after parsing error: %s", row["url"], exc)

    if not items_by_url:
        raise RuntimeError("Scraper completed but did not produce catalog items.")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps([item.model_dump(mode="json") for item in items_by_url.values()], indent=2),
        encoding="utf-8",
    )
    logger.info("Wrote %d catalog records to %s", len(items_by_url), output)
    return list(items_by_url.values())


if __name__ == "__main__":
    scrape_catalog()

