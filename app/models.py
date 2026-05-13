from enum import StrEnum


class JobStatus(StrEnum):
    NEW = "new"
    SEEN = "seen"
    INTERESTING = "interesting"
    APPLIED = "applied"
    IGNORED = "ignored"
    EXPIRED = "expired"
