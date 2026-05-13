from app.database import JobRepository, init_db
from app.schemas import JobCreate


def test_jobs_are_listed_by_highest_score_first(tmp_path) -> None:
    database_path = str(tmp_path / "jobs.db")
    init_db(database_path)
    repository = JobRepository(database_path)

    repository.add(
        JobCreate(
            source_name="test",
            title="Lower score",
            company="Example AG",
            location="Bern",
            url="https://example.com/lower",
            matched_keywords=["Supporter"],
            score=5,
            content_hash="lower",
        )
    )
    repository.add(
        JobCreate(
            source_name="test",
            title="Higher score",
            company="Example AG",
            location="Bern",
            url="https://example.com/higher",
            matched_keywords=["Junior", "Supporter"],
            score=10,
            content_hash="higher",
        )
    )

    jobs = repository.list()

    assert [job.title for job in jobs] == ["Higher score", "Lower score"]
