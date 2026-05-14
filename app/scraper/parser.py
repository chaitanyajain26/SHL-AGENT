from __future__ import annotations

from urllib.parse import urljoin
from bs4 import BeautifulSoup
from app.models.catalog_models import CatalogItem
from app.utils.helpers import unique_preserve_order


TYPE_MAP = {
    "A": "Ability & Aptitude",
    "B": "Biodata & Situational Judgment",
    "C": "Competencies",
    "D": "Development & 360",
    "E": "English Language",
    "K": "Knowledge & Skills",
    "P": "Personality & Behavior",
    "S": "Simulation",
}


def infer_test_type(text: str) -> str:
    lower = text.lower()
    if any(word in lower for word in ["java", "python", "sql", "coding", "technology", "programming"]):
        return "K"
    if any(word in lower for word in ["personality", "opq", "motivation", "behavior", "behaviour"]):
        return "P"
    if any(word in lower for word in ["numerical", "verbal", "inductive", "deductive", "cognitive", "ability", "gsa"]):
        return "A"
    if any(word in lower for word in ["simulation", "call center", "contact center"]):
        return "S"
    return "K"


def extract_keywords(*values: str) -> list[str]:
    source = " ".join(values).lower()
    candidates = [
        "java", "python", "sql", "javascript", "coding", "developer", "software",
        "sales", "manager", "leadership", "graduate", "personality", "opq",
        "numerical", "verbal", "deductive", "inductive", "contact center",
        "customer service", "remote", "finance", "administrative", "microsoft",
    ]
    return [keyword for keyword in candidates if keyword in source]


def parse_catalog_listing(html: str, base_url: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    rows: list[dict[str, str]] = []
    for link in soup.select("a[href*='product-catalog']"):
        name = " ".join(link.get_text(" ", strip=True).split())
        href = link.get("href")
        if not name or not href or len(name) < 3:
            continue
        url = urljoin(base_url, href)
        if "/products/product-catalog/" not in url:
            continue
        surrounding = link.find_parent(["tr", "li", "article", "div"])
        text = surrounding.get_text(" ", strip=True) if surrounding else name
        rows.append({"name": name, "url": url, "summary": text})
    return rows


def parse_assessment_page(name: str, url: str, html: str, fallback_text: str = "") -> CatalogItem:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find(["h1", "h2"])
    clean_name = " ".join((title.get_text(" ", strip=True) if title else name).split()) or name
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    description = next((p for p in paragraphs if len(p) > 60), fallback_text or clean_name)
    page_text = soup.get_text(" ", strip=True)
    duration = ""
    for label in ["Approximate Completion Time", "Duration", "Time"]:
        if label.lower() in page_text.lower():
            duration = label
            break
    test_type = infer_test_type(f"{clean_name} {description} {page_text}")
    keywords = unique_preserve_order(extract_keywords(clean_name, description, page_text))
    category = TYPE_MAP.get(test_type, "Assessment")
    remote_testing = "remote" in page_text.lower() or "online" in page_text.lower() or True
    return CatalogItem(
        name=clean_name,
        url=url,
        description=description,
        duration=duration,
        test_type=test_type,
        keywords=keywords,
        category=category,
        remote_testing=remote_testing,
    )

