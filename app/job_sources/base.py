from abc import ABC, abstractmethod

from app.schemas import RawJobListing, SourceConfig


class JobSource(ABC):
    def __init__(self, config: SourceConfig) -> None:
        self.config = config

    @abstractmethod
    async def fetch_jobs(self) -> list[RawJobListing]:
        raise NotImplementedError
