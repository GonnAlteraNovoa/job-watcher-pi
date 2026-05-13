# Job Watcher Pi

Job Watcher Pi is a lightweight self-hosted job monitoring backend for a Raspberry Pi homelab. It scans configured job boards and career pages, normalizes listings, scores them against your keywords and locations, stores them in SQLite, and returns only newly discovered matching jobs to automation tools like n8n.

The MVP intentionally avoids browser automation and LinkedIn scraping. It starts with simple HTTP fetching plus BeautifulSoup parsing so it stays practical on low-power hardware.

## Architecture

- **FastAPI backend** exposes a small HTTP API for n8n and manual use.
- **SQLite** stores discovered jobs and deduplication state in `/data/jobs.db`.
- **YAML config** defines keywords, score thresholds, locations, and job sources.
- **Generic HTML source adapter** supports job pages where listings can be extracted with CSS selectors.
- **n8n** handles cron scheduling, orchestration, and Telegram/email notifications.
- **Docker Compose** makes deployment through Portainer straightforward.

## Why n8n + FastAPI

n8n is already good at scheduling, retries, branching, and notifications. The FastAPI service stays focused on the parts that need custom code: fetching, parsing, matching, scoring, deduplication, and persistence. This keeps the Raspberry Pi workload small while making the project easier to extend.

## Quick Start

1. Copy the example environment and source config:

```bash
cp .env.example .env
cp data/sources.example.yml data/sources.yml
```

2. Edit `data/sources.yml` with real sources and CSS selectors.

3. Start the service:

```bash
docker compose up -d --build
```

4. Check health:

```bash
curl http://localhost:8088/health
```

The API will be available on `http://<raspberry-pi-ip>:8088`.

## Portainer Setup

1. Create a new stack in Portainer.
2. Paste or upload `docker-compose.yml`.
3. Make sure the project directory contains `.env` and `data/sources.yml`.
4. Deploy the stack.
5. Confirm the container health check is passing.

## Configuration

`CONFIG_PATH` defaults to `/data/sources.yml` in Docker. A source uses CSS selectors to extract job cards:

```yaml
filters:
  keywords:
    - junior
    - ICT Support
    - IT Support
  negative_keywords:
    - senior
    - manager
  preferred_locations:
    - Bern
    - Zürich
    - Remote Switzerland
  minimum_score: 5

sources:
  - name: Example Careers
    type: generic_html
    enabled: true
    url: https://example.com/careers
    selectors:
      job_card: ".job"
      title: ".job-title"
      company: ".company"
      location: ".location"
      link: "a"
      description: ".description"
```

Use `data/sources.example.yml` as the editable starting point. Some modern job boards render listings with JavaScript; leave those for a future Playwright source adapter.

## API Examples

Run a scan and return only new matching jobs:

```bash
curl -X POST http://localhost:8088/scan
```

List stored jobs:

```bash
curl "http://localhost:8088/jobs"
```

Filter by status:

```bash
curl "http://localhost:8088/jobs?status=interesting"
```

Filter by keyword:

```bash
curl "http://localhost:8088/jobs?keyword=support"
```

Update job status:

```bash
curl -X PATCH http://localhost:8088/jobs/1/status \
  -H "Content-Type: application/json" \
  -d '{"status":"interesting"}'
```

## n8n Workflow

Create this workflow:

1. **Cron Trigger** every 30 minutes.
2. **HTTP Request** node:
   - Method: `POST`
   - URL: `http://job-watcher-pi:8088/scan` if n8n is on the same Docker network, or `http://<pi-ip>:8088/scan`.
3. **IF** node:
   - Check whether `new_jobs.length > 0`.
4. **Telegram** or **Email** node:
   - Send one message per job or a summarized digest.

Suggested notification format:

```text
New job match: {{title}} at {{company}} - {{location}} - Score: {{score}} - {{url}}
```

The `/scan` response contains `new_jobs`, so n8n can branch cleanly without tracking state itself.

## Development

Install dependencies:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
```

Run locally:

```bash
CONFIG_PATH=data/sources.example.yml DATABASE_PATH=data/jobs.db uvicorn app.main:app --reload --port 8088
```

Run tests:

```bash
pytest
```

## Roadmap

- Telegram buttons for `interesting`, `applied`, and `ignored`.
- Small web dashboard for reviewing jobs.
- Playwright-based source adapter for JavaScript-heavy pages.
- AI job summarizer.
- CV matching against job descriptions.
- Multi-user support.
- Export to CSV.
- Browser extension or bookmarklet for manually saving jobs.
