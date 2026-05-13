from fastapi import APIRouter, Depends, HTTPException, Query

from app.config import get_settings, load_app_config
from app.database import JobRepository
from app.models import JobStatus
from app.schemas import JobRead, ScanResponse, StatusUpdate
from app.services.fetcher import HttpFetcher
from app.services.job_service import JobService


router = APIRouter()


def get_repository() -> JobRepository:
    settings = get_settings()
    return JobRepository(settings.database_path)


def get_job_service(repository: JobRepository = Depends(get_repository)) -> JobService:
    settings = get_settings()
    fetcher = HttpFetcher(settings.request_timeout_seconds, settings.user_agent)
    return JobService(repository, fetcher)


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/scan", response_model=ScanResponse)
async def scan(job_service: JobService = Depends(get_job_service)) -> ScanResponse:
    config = load_app_config()
    return await job_service.scan(config)


@router.get("/jobs", response_model=list[JobRead])
def list_jobs(
    status: JobStatus | None = Query(default=None),
    keyword: str | None = Query(default=None),
    repository: JobRepository = Depends(get_repository),
) -> list[JobRead]:
    return repository.list(status=status, keyword=keyword)


@router.patch("/jobs/{job_id}/status", response_model=JobRead)
def update_job_status(
    job_id: int,
    update: StatusUpdate,
    repository: JobRepository = Depends(get_repository),
) -> JobRead:
    job = repository.update_status(job_id, update.status)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
