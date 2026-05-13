from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl

from app.models import JobStatus


class SourceSelectors(BaseModel):
    job_card: str
    title: str
    company: str | None = None
    location: str | None = None
    link: str
    description: str | None = None


class SourceConfig(BaseModel):
    name: str
    type: str = "generic_html"
    enabled: bool = True
    url: HttpUrl
    selectors: SourceSelectors


class FilterConfig(BaseModel):
    keywords: list[str] = Field(default_factory=list)
    negative_keywords: list[str] = Field(default_factory=list)
    preferred_locations: list[str] = Field(default_factory=list)
    minimum_score: int = 1


class AppConfigFile(BaseModel):
    filters: FilterConfig = Field(default_factory=FilterConfig)
    sources: list[SourceConfig] = Field(default_factory=list)


class RawJobListing(BaseModel):
    source_name: str
    title: str
    company: str | None = None
    location: str | None = None
    url: str
    description: str | None = None
    date_posted: datetime | None = None


class MatchResult(BaseModel):
    matched_keywords: list[str]
    score: int
    is_match: bool


class JobCreate(RawJobListing):
    matched_keywords: list[str]
    score: int
    content_hash: str
    status: JobStatus = JobStatus.NEW


class JobRead(BaseModel):
    id: int
    source_name: str
    title: str
    company: str | None
    location: str | None
    url: str
    date_found: datetime
    date_posted: datetime | None
    description: str | None
    matched_keywords: list[str]
    score: int
    content_hash: str
    status: JobStatus


class StatusUpdate(BaseModel):
    status: JobStatus


class ScanResponse(BaseModel):
    scanned_sources: int
    fetched_jobs: int
    matched_jobs: int
    new_jobs: list[JobRead]
    errors: list[dict[str, Any]] = Field(default_factory=list)
