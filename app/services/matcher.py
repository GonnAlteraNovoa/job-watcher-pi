import re

from app.schemas import FilterConfig, MatchResult, RawJobListing


def score_job(job: RawJobListing, filters: FilterConfig) -> MatchResult:
    title = job.title or ""
    description = job.description or ""
    location = job.location or ""
    matched_keywords: set[str] = set()
    score = 0

    for keyword in filters.keywords:
        if _contains_term(title, keyword):
            score += 5
            matched_keywords.add(keyword)
        if description and _contains_term(description, keyword):
            score += 2
            matched_keywords.add(keyword)

    for preferred_location in filters.preferred_locations:
        if _contains_term(location, preferred_location):
            score += 3
            matched_keywords.add(preferred_location)
            break

    combined_text = " ".join([title, description, location])
    for negative_keyword in filters.negative_keywords:
        if _contains_term(combined_text, negative_keyword):
            score -= 5

    return MatchResult(
        matched_keywords=sorted(matched_keywords, key=str.lower),
        score=score,
        is_match=score >= filters.minimum_score,
    )


def _contains_term(text: str, term: str) -> bool:
    if not text or not term:
        return False
    pattern = rf"(?<!\w){re.escape(term.lower())}(?!\w)"
    return re.search(pattern, text.lower()) is not None
