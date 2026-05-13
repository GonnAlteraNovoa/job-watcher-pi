import hashlib
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from app.schemas import RawJobListing


TRACKING_PARAMS_PREFIXES = ("utm_",)
TRACKING_PARAMS = {"fbclid", "gclid", "msclkid"}


def canonicalize_url(url: str) -> str:
    split = urlsplit(url.strip())
    scheme = split.scheme.lower() or "https"
    netloc = split.netloc.lower()
    path = split.path.rstrip("/") or "/"
    query_items = [
        (key, value)
        for key, value in parse_qsl(split.query, keep_blank_values=True)
        if key not in TRACKING_PARAMS and not key.startswith(TRACKING_PARAMS_PREFIXES)
    ]
    query = urlencode(sorted(query_items))
    return urlunsplit((scheme, netloc, path, query, ""))


def content_hash(job: RawJobListing) -> str:
    parts = [
        normalize_text(job.title),
        normalize_text(job.company or ""),
        normalize_text(job.location or ""),
    ]
    digest_input = "|".join(parts)
    return hashlib.sha256(digest_input.encode("utf-8")).hexdigest()


def normalize_text(value: str) -> str:
    return " ".join(value.casefold().split())
