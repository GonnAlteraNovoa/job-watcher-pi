from app.job_sources.generic_html import parse_generic_html
from app.schemas import SourceConfig


def test_optional_selectors_return_empty_strings() -> None:
    config = SourceConfig.model_validate(
        {
            "name": "test",
            "url": "https://example.com/jobs",
            "selectors": {
                "job_card": "article",
                "title": "h2",
                "company": "",
                "location": "",
                "link": "a",
                "description": "",
            },
        }
    )
    html = """
    <article>
      <h2><a href="/jobs/1">Junior IT Support</a></h2>
    </article>
    """

    jobs = parse_generic_html(html, config)

    assert len(jobs) == 1
    assert jobs[0].company == ""
    assert jobs[0].location == ""
    assert jobs[0].description == ""


def test_empty_title_selector_uses_card_text() -> None:
    config = SourceConfig.model_validate(
        {
            "name": "test",
            "url": "https://example.com/jobs",
            "selectors": {
                "job_card": "article",
                "title": "",
                "link": "a",
            },
        }
    )
    html = '<article><a href="/jobs/1">Junior IT Support Bern</a></article>'

    jobs = parse_generic_html(html, config)

    assert jobs[0].title == "Junior IT Support Bern"


def test_link_falls_back_to_card_href_when_card_is_anchor() -> None:
    config = SourceConfig.model_validate(
        {
            "name": "test",
            "url": "https://example.com/jobs",
            "selectors": {
                "job_card": "a.job-card",
                "title": "",
                "link": ".missing-link",
            },
        }
    )
    html = '<a class="job-card" href="/jobs/1">Junior IT Support Bern</a>'

    jobs = parse_generic_html(html, config)

    assert jobs[0].url == "https://example.com/jobs/1"
