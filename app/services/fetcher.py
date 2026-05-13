import logging

import httpx


logger = logging.getLogger(__name__)


class HttpFetcher:
    def __init__(self, timeout_seconds: float, user_agent: str) -> None:
        self.timeout_seconds = timeout_seconds
        self.user_agent = user_agent

    async def get(self, url: str) -> str:
        headers = {"User-Agent": self.user_agent}
        timeout = httpx.Timeout(self.timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=headers) as client:
            response = await client.get(url)
            response.raise_for_status()
            logger.debug("Fetched %s with status %s", url, response.status_code)
            return response.text
