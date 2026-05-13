import logging
from typing import Any

from pydantic import HttpUrl

from app.database import JobRepository
from app.job_sources.generic_html import GenericHtmlSource
from app.schemas import AppConfigFile, JobCreate, RawJobListing, ScanResponse, SourceConfig
from app.services.deduplicator import canonicalize_url, content_hash
from app.services.fetcher import HttpFetcher
from app.services.matcher import score_job


logger = logging.getLogger(__name__)


class JobService:
    def __init__(self, repository: JobRepository, fetcher: HttpFetcher) -> None:
        self.repository = repository
        self.fetcher = fetcher

    async def scan(self, config: AppConfigFile) -> ScanResponse:
        fetched_jobs = 0
        matched_jobs = 0
        new_jobs = []
        errors: list[dict[str, Any]] = []
        enabled_sources = [source for source in config.sources if source.enabled]

        for source_config in enabled_sources:
            try:
                source = self._build_source(source_config)
                raw_jobs = await source.fetch_jobs()
                fetched_jobs += len(raw_jobs)
            except Exception as exc:
                logger.exception("Failed to scan source %s", source_config.name)
                errors.append({"source": source_config.name, "error": str(exc)})
                continue

            for raw_job in raw_jobs:
                normalized_job = _normalize_job_url(raw_job)
                match = score_job(normalized_job, config.filters)
                if not match.is_match:
                    continue

                matched_jobs += 1
                digest = content_hash(normalized_job)
                if self.repository.exists(normalized_job.url, digest):
                    continue

                created_job = self.repository.add(
                    JobCreate(
                        **normalized_job.model_dump(),
                        matched_keywords=match.matched_keywords,
                        score=match.score,
                        content_hash=digest,
                    )
                )
                new_jobs.append(created_job)

        return ScanResponse(
            scanned_sources=len(enabled_sources),
            fetched_jobs=fetched_jobs,
            matched_jobs=matched_jobs,
            new_jobs=new_jobs,
            errors=errors,
        )

    def _build_source(self, source_config: SourceConfig) -> GenericHtmlSource:
        if source_config.type != "generic_html":
            raise ValueError(f"Unsupported source type: {source_config.type}")
        return GenericHtmlSource(source_config, self.fetcher)


def _normalize_job_url(job: RawJobListing) -> RawJobListing:
    data = job.model_dump()
    data["url"] = canonicalize_url(job.url)
    return RawJobListing(**data)
