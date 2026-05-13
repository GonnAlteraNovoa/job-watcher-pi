from app.schemas import FilterConfig, RawJobListing
from app.services.matcher import score_job


def test_scores_title_description_and_location_matches() -> None:
    filters = FilterConfig(
        keywords=["IT Support", "Junior"],
        negative_keywords=["senior"],
        preferred_locations=["Bern"],
        minimum_score=5,
    )
    job = RawJobListing(
        source_name="test",
        title="Junior IT Support Specialist",
        company="Example AG",
        location="Bern",
        url="https://example.com/job",
        description="Help users as part of the IT Support team.",
    )

    result = score_job(job, filters)

    assert result.is_match is True
    assert result.score == 15
    assert result.matched_keywords == ["Bern", "IT Support", "Junior"]


def test_negative_keywords_reduce_score() -> None:
    filters = FilterConfig(
        keywords=["IT Support"],
        negative_keywords=["senior", "manager"],
        preferred_locations=[],
        minimum_score=5,
    )
    job = RawJobListing(
        source_name="test",
        title="Senior IT Support Manager",
        company="Example AG",
        location="Zürich",
        url="https://example.com/job",
        description=None,
    )

    result = score_job(job, filters)

    assert result.score == -5
    assert result.is_match is False
