from html import escape

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse

from app.api.routes import get_repository
from app.database import JobRepository
from app.models import JobStatus
from app.schemas import JobRead


router = APIRouter()


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def redirect_dashboard() -> HTMLResponse:
    return HTMLResponse(
        '<!doctype html><meta http-equiv="refresh" content="0; url=/dashboard">'
        '<a href="/dashboard">Open dashboard</a>'
    )


@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
def dashboard(
    status: JobStatus | None = Query(default=None),
    keyword: str | None = Query(default=None),
    repository: JobRepository = Depends(get_repository),
) -> HTMLResponse:
    jobs = repository.list(status=status, keyword=keyword)
    return HTMLResponse(_render_dashboard(jobs, status, keyword))


def _render_dashboard(jobs: list[JobRead], status: JobStatus | None, keyword: str | None) -> str:
    status_options = "".join(
        f'<option value="{item.value}" {_selected(status, item)}>{escape(item.value.title())}</option>'
        for item in JobStatus
    )
    job_rows = "\n".join(_render_job_card(job) for job in jobs)
    empty_state = (
        '<section class="empty">No jobs match the current filters.</section>'
        if not jobs
        else ""
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Job Watcher Pi</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --border: #d9dee7;
      --text: #17202a;
      --muted: #667085;
      --accent: #2563eb;
      --accent-soft: #dbeafe;
      --accent-text: #1d4ed8;
      --control-bg: #ffffff;
      --button-bg: #17202a;
      --button-text: #ffffff;
      --description: #344054;
      --good: #047857;
      --warn: #b45309;
      --bad: #b91c1c;
    }}
    :root[data-theme="dark"] {{
      color-scheme: dark;
      --bg: #101418;
      --panel: #181d23;
      --border: #303946;
      --text: #eef2f6;
      --muted: #a0acba;
      --accent: #60a5fa;
      --accent-soft: #1e3a5f;
      --accent-text: #bfdbfe;
      --control-bg: #111820;
      --button-bg: #eef2f6;
      --button-text: #111820;
      --description: #cbd5e1;
      --good: #34d399;
      --warn: #fbbf24;
      --bad: #f87171;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 16px;
      line-height: 1.45;
    }}
    header {{
      background: var(--panel);
      border-bottom: 1px solid var(--border);
    }}
    .wrap {{
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
    }}
    .topbar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 18px 0;
    }}
    .title-block {{
      display: grid;
      gap: 2px;
    }}
    h1 {{
      margin: 0;
      font-size: 1.35rem;
      font-weight: 750;
    }}
    .count {{
      color: var(--muted);
      font-size: 0.95rem;
      white-space: nowrap;
    }}
    .header-actions {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .theme-toggle {{
      width: auto;
      min-height: 38px;
      border-radius: 999px;
      padding: 0 14px;
      background: var(--control-bg);
      color: var(--text);
      border-color: var(--border);
      white-space: nowrap;
    }}
    form.filters {{
      display: grid;
      grid-template-columns: 1fr 180px auto;
      gap: 10px;
      padding: 0 0 18px;
    }}
    input, select, button {{
      width: 100%;
      min-height: 42px;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 0 12px;
      background: var(--control-bg);
      color: var(--text);
      font: inherit;
    }}
    button {{
      cursor: pointer;
      background: var(--button-bg);
      color: var(--button-text);
      border-color: var(--button-bg);
      font-weight: 650;
    }}
    main {{
      padding: 18px 0 36px;
    }}
    .jobs {{
      display: grid;
      gap: 12px;
    }}
    article.job {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 160px;
      gap: 16px;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
    }}
    .title-row {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
      margin-bottom: 6px;
    }}
    h2 {{
      margin: 0;
      font-size: 1.05rem;
      line-height: 1.3;
    }}
    h2 a {{
      color: var(--text);
      text-decoration: none;
    }}
    h2 a:hover {{
      color: var(--accent);
      text-decoration: underline;
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      border-radius: 999px;
      padding: 2px 9px;
      background: var(--accent-soft);
      color: var(--accent-text);
      font-size: 0.82rem;
      font-weight: 700;
      white-space: nowrap;
    }}
    .meta, .source, .found, .keywords {{
      color: var(--muted);
      font-size: 0.92rem;
    }}
    .meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px 14px;
      margin-bottom: 8px;
    }}
    .description {{
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
      color: var(--description);
      margin-top: 10px;
      font-size: 0.95rem;
    }}
    .actions {{
      display: grid;
      align-content: start;
      gap: 8px;
    }}
    .status {{
      min-height: 38px;
      font-size: 0.93rem;
    }}
    .open-link {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 38px;
      border-radius: 8px;
      background: var(--accent);
      color: #fff;
      text-decoration: none;
      font-weight: 700;
      font-size: 0.93rem;
    }}
    .empty {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 24px;
      color: var(--muted);
      text-align: center;
    }}
    @media (max-width: 720px) {{
      .wrap {{
        width: min(100% - 20px, 1120px);
      }}
      .topbar {{
        align-items: stretch;
        flex-direction: column;
        gap: 10px;
      }}
      .header-actions {{
        justify-content: space-between;
      }}
      form.filters {{
        grid-template-columns: 1fr;
      }}
      article.job {{
        grid-template-columns: 1fr;
        gap: 12px;
        padding: 14px;
      }}
      .actions {{
        grid-template-columns: 1fr 1fr;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <div class="topbar">
        <div class="title-block">
          <h1>Job Watcher Pi</h1>
          <div class="count">{len(jobs)} jobs shown</div>
        </div>
        <div class="header-actions">
          <button class="theme-toggle" type="button" id="theme-toggle" aria-label="Toggle dark mode">Dark mode</button>
        </div>
      </div>
      <form class="filters" method="get" action="/dashboard">
        <input name="keyword" value="{escape(keyword or "")}" placeholder="Filter by keyword">
        <select name="status">
          <option value="">All statuses</option>
          {status_options}
        </select>
        <button type="submit">Filter</button>
      </form>
    </div>
  </header>
  <main class="wrap">
    <section class="jobs">
      {job_rows}
    </section>
    {empty_state}
  </main>
  <script>
    const root = document.documentElement;
    const themeToggle = document.getElementById("theme-toggle");

    function preferredTheme() {{
      const savedTheme = localStorage.getItem("job-watcher-theme");
      if (savedTheme === "light" || savedTheme === "dark") {{
        return savedTheme;
      }}
      return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }}

    function applyTheme(theme) {{
      root.dataset.theme = theme;
      themeToggle.textContent = theme === "dark" ? "Light mode" : "Dark mode";
      themeToggle.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
    }}

    applyTheme(preferredTheme());

    themeToggle.addEventListener("click", () => {{
      const nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
      localStorage.setItem("job-watcher-theme", nextTheme);
      applyTheme(nextTheme);
    }});

    async function updateStatus(select) {{
      const jobId = select.dataset.jobId;
      select.disabled = true;
      try {{
        const response = await fetch(`/jobs/${{jobId}}/status`, {{
          method: "PATCH",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify({{ status: select.value }})
        }});
        if (!response.ok) {{
          throw new Error("Status update failed");
        }}
      }} catch (error) {{
        alert(error.message);
      }} finally {{
        select.disabled = false;
      }}
    }}
  </script>
</body>
</html>"""


def _render_job_card(job: JobRead) -> str:
    company = escape(job.company or "Unknown company")
    location = escape(job.location or "Unknown location")
    description = escape(job.description or "")
    keywords = ", ".join(escape(keyword) for keyword in job.matched_keywords)
    status_options = "".join(
        f'<option value="{item.value}" {_selected(job.status, item)}>{escape(item.value.title())}</option>'
        for item in JobStatus
    )
    found = job.date_found.strftime("%Y-%m-%d %H:%M")

    return f"""<article class="job">
  <div>
    <div class="title-row">
      <h2><a href="{escape(job.url)}" target="_blank" rel="noopener noreferrer">{escape(job.title)}</a></h2>
      <span class="badge">Score {job.score}</span>
    </div>
    <div class="meta">
      <span>{company}</span>
      <span>{location}</span>
    </div>
    <div class="source">{escape(job.source_name)} · Found {escape(found)}</div>
    <div class="keywords">Matched: {keywords or "none"}</div>
    {_description_block(description)}
  </div>
  <div class="actions">
    <select class="status" data-job-id="{job.id}" onchange="updateStatus(this)">
      {status_options}
    </select>
    <a class="open-link" href="{escape(job.url)}" target="_blank" rel="noopener noreferrer">Open</a>
  </div>
</article>"""


def _description_block(description: str) -> str:
    if not description:
        return ""
    return f'<div class="description">{description}</div>'


def _selected(current: JobStatus | None, item: JobStatus) -> str:
    return "selected" if current == item else ""
