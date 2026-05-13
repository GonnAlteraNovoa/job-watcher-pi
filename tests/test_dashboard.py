from datetime import UTC, datetime

from app.api.dashboard import _render_dashboard
from app.models import JobStatus
from app.schemas import JobRead


def test_dashboard_renders_jobs_and_status_controls() -> None:
    html = _render_dashboard(
        [
            JobRead(
                id=1,
                source_name="test",
                title="Junior IT Support",
                company="Example AG",
                location="Bern",
                url="https://example.com/job",
                date_found=datetime(2026, 5, 13, 10, 0, tzinfo=UTC),
                date_posted=None,
                description="Support users and hardware.",
                matched_keywords=["junior", "IT Support"],
                score=10,
                content_hash="abc",
                status=JobStatus.NEW,
            )
        ],
        status=None,
        keyword=None,
    )

    assert "Job Watcher Pi" in html
    assert "Junior IT Support" in html
    assert "Example AG" in html
    assert 'data-job-id="1"' in html
    assert "/jobs/${jobId}/status" in html
