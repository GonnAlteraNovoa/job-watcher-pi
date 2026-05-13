from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from app.job_sources.base import JobSource
from app.schemas import RawJobListing, SourceConfig
from app.services.fetcher import HttpFetcher


class GenericHtmlSource(JobSource):
    def __init__(self, config: SourceConfig, fetcher: HttpFetcher) -> None:
        super().__init__(config)
        self.fetcher = fetcher

    async def fetch_jobs(self) -> list[RawJobListing]:
        html = await self.fetcher.get(str(self.config.url))
        return parse_generic_html(html, self.config)


def parse_generic_html(html: str, config: SourceConfig) -> list[RawJobListing]:
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select(config.selectors.job_card)
    jobs: list[RawJobListing] = []

    for card in cards:
        title = _select_text(card, config.selectors.title)
        link = _select_link(card, config.selectors.link, str(config.url))
        if not title or not link:
            continue

        jobs.append(
            RawJobListing(
                source_name=config.name,
                title=title,
                company=_select_text(card, config.selectors.company),
                location=_select_text(card, config.selectors.location),
                url=link,
                description=_select_text(card, config.selectors.description),
            )
        )

    return jobs


def _select_text(card: Tag, selector: str | None) -> str | None:
    if not selector:
        return None
    element = card.select_one(selector)
    if not element:
        return None
    text = element.get_text(" ", strip=True)
    return text or None


def _select_link(card: Tag, selector: str, base_url: str) -> str | None:
    element = card.select_one(selector)
    if not element:
        return None
    href = element.get("href")
    if not href:
        return None
    return urljoin(base_url, str(href))
