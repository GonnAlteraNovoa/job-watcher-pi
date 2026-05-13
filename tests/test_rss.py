from app.job_sources.rss import parse_rss
from app.schemas import SourceConfig


def test_parse_rss_extracts_swissdevjobs_title_company_and_location() -> None:
    config = SourceConfig.model_validate(
        {
            "name": "SwissDevJobs RSS",
            "type": "rss",
            "url": "https://swissdevjobs.ch/rss",
        }
    )
    xml = """
    <rss>
      <channel>
        <item>
          <title><![CDATA[IT-Systemtechniker (m/w) @ KMU Informatikpartner AG [CHF 65'000 - 90'000]]]></title>
          <link>https://swissdevjobs.ch/jobs/KMU-Informatikpartner-AG-IT-Systemtechniker-mw?utm_source=our_rss_feed</link>
          <pubDate>Mon, 11 May 2026 10:00:00 GMT</pubDate>
          <description><![CDATA[
            Requirements:
              * Support Erfahrung
            More:
            Arbeitsort: Bern, Hybrid
          ]]></description>
        </item>
      </channel>
    </rss>
    """

    jobs = parse_rss(xml, config)

    assert len(jobs) == 1
    assert jobs[0].title == "IT-Systemtechniker (m/w)"
    assert jobs[0].company == "KMU Informatikpartner AG"
    assert jobs[0].location == "Bern, Hybrid"
    assert "Support Erfahrung" in (jobs[0].description or "")
    assert jobs[0].date_posted is not None
