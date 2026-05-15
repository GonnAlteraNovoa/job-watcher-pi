import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from app.models import JobStatus
from app.schemas import JobCreate, JobRead


def get_connection(database_path: str) -> sqlite3.Connection:
    Path(database_path).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def connection_context(database_path: str) -> Iterator[sqlite3.Connection]:
    connection = get_connection(database_path)
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db(database_path: str) -> None:
    with connection_context(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT NOT NULL,
                title TEXT NOT NULL,
                company TEXT,
                location TEXT,
                url TEXT NOT NULL,
                date_found TEXT NOT NULL,
                date_posted TEXT,
                description TEXT,
                matched_keywords TEXT NOT NULL,
                score INTEGER NOT NULL,
                content_hash TEXT NOT NULL,
                status TEXT NOT NULL,
                UNIQUE(url),
                UNIQUE(content_hash)
            )
            """
        )
        connection.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_jobs_score ON jobs(score)")


def row_to_job(row: sqlite3.Row) -> JobRead:
    return JobRead(
        id=row["id"],
        source_name=row["source_name"],
        title=row["title"],
        company=row["company"],
        location=row["location"],
        url=row["url"],
        date_found=datetime.fromisoformat(row["date_found"]),
        date_posted=datetime.fromisoformat(row["date_posted"]) if row["date_posted"] else None,
        description=row["description"],
        matched_keywords=json.loads(row["matched_keywords"]),
        score=row["score"],
        content_hash=row["content_hash"],
        status=JobStatus(row["status"]),
    )


class JobRepository:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path

    def exists(self, url: str, content_hash: str) -> bool:
        with connection_context(self.database_path) as connection:
            row = connection.execute(
                "SELECT id FROM jobs WHERE url = ? OR content_hash = ? LIMIT 1",
                (url, content_hash),
            ).fetchone()
            return row is not None

    def get(self, job_id: int) -> JobRead | None:
        with connection_context(self.database_path) as connection:
            row = connection.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            return row_to_job(row) if row else None

    def add(self, job: JobCreate) -> JobRead:
        now = datetime.now(UTC).isoformat()
        with connection_context(self.database_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO jobs (
                    source_name, title, company, location, url, date_found, date_posted,
                    description, matched_keywords, score, content_hash, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job.source_name,
                    job.title,
                    job.company,
                    job.location,
                    job.url,
                    now,
                    job.date_posted.isoformat() if job.date_posted else None,
                    job.description,
                    json.dumps(job.matched_keywords),
                    job.score,
                    job.content_hash,
                    job.status.value,
                ),
            )
            row = connection.execute("SELECT * FROM jobs WHERE id = ?", (cursor.lastrowid,)).fetchone()
            return row_to_job(row)

    def list(self, status: JobStatus | None = None, keyword: str | None = None) -> list[JobRead]:
        query = "SELECT * FROM jobs"
        clauses: list[str] = []
        params: list[str] = []

        if status:
            clauses.append("status = ?")
            params.append(status.value)
        if keyword:
            like_keyword = f"%{keyword.lower()}%"
            clauses.append(
                "(lower(title) LIKE ? OR lower(description) LIKE ? OR lower(matched_keywords) LIKE ?)"
            )
            params.extend([like_keyword, like_keyword, like_keyword])

        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY score DESC, date_found DESC"

        with connection_context(self.database_path) as connection:
            rows = connection.execute(query, params).fetchall()
            return [row_to_job(row) for row in rows]

    def update_status(self, job_id: int, status: JobStatus) -> JobRead | None:
        with connection_context(self.database_path) as connection:
            connection.execute("UPDATE jobs SET status = ? WHERE id = ?", (status.value, job_id))
            row = connection.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            return row_to_job(row) if row else None
