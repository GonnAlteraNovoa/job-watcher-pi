from app.schemas import RawJobListing
from app.services.deduplicator import canonicalize_url, content_hash


def test_canonicalize_url_removes_tracking_and_fragment() -> None:
    url = "HTTPS://Example.com/jobs/123/?utm_source=x&b=2&a=1#details"

    assert canonicalize_url(url) == "https://example.com/jobs/123?a=1&b=2"


def test_content_hash_uses_title_company_and_location() -> None:
    first = RawJobListing(
        source_name="a",
        title=" Junior IT Support ",
        company="Example AG",
        location="Bern",
        url="https://example.com/a",
    )
    second = RawJobListing(
        source_name="b",
        title="junior   it support",
        company="example ag",
        location="Bern",
        url="https://example.com/b",
    )

    assert content_hash(first) == content_hash(second)
