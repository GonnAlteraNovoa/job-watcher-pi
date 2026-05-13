from datetime import datetime
from email.utils import parsedate_to_datetime
import re
import xml.etree.ElementTree as ET

from app.job_sources.base import JobSource
from app.schemas import RawJobListing, SourceConfig
from app.services.fetcher import HttpFetcher


class RssSource(JobSource):
    def __init__(self, config: SourceConfig, fetcher: HttpFetcher) -> None:
        super().__init__(config)
        self.fetcher = fetcher

    async def fetch_jobs(self) -> list[RawJobListing]:
        xml_text = await self.fetcher.get(str(self.config.url))
        return parse_rss(xml_text, self.config)


def parse_rss(xml_text: str, config: SourceConfig) -> list[RawJobListing]:
    root = ET.fromstring(xml_text)
    items = root.findall(".//item")
    jobs: list[RawJobListing] = []

    for item in items:
        raw_title = _item_text(item, "title")
        url = _item_text(item, "link") or _item_text(item, "guid")
        if not raw_title or not url:
            continue

        title, company = _split_swissdevjobs_title(raw_title)
        description = _item_text(item, "description")

        jobs.append(
            RawJobListing(
                source_name=config.name,
                title=title,
                company=company,
                location=_extract_location(description),
                url=url,
                description=description,
                date_posted=_parse_pub_date(_item_text(item, "pubDate")),
            )
        )

    return jobs


def _item_text(item: ET.Element, tag: str) -> str:
    element = item.find(tag)
    if element is None or element.text is None:
        return ""
    return element.text.strip()


def _split_swissdevjobs_title(raw_title: str) -> tuple[str, str]:
    title_without_salary = re.sub(r"\s*\[[^\]]+\]\s*$", "", raw_title).strip()
    if " @ " not in title_without_salary:
        return title_without_salary, ""

    title, company = title_without_salary.rsplit(" @ ", 1)
    return title.strip(), company.strip()


def _extract_location(description: str) -> str:
    patterns = [
        r"Arbeitsort:\s*([^\n\r<]+)",
        r"Arbeitsort\s+([^\n\r<]+)",
        r"\b(Bern|Zürich|Zurich|Basel|Luzern|Solothurn|Biel|Thun|Remote)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, description, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip(" .,-")
    return ""


def _parse_pub_date(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
