# IncidentDesk

**DFIR case management platform for incident tracking, investigation notes, IOC linkage, and reporting.**

IncidentDesk is a lightweight, defensive DFIR Case Manager designed for SOC/IR analyst workflows.
It helps structure investigations from first alert to final report, without offensive features or enterprise bloat.

## Why This Project Exists
- Provide a realistic portfolio-grade DFIR case management app.
- Demonstrate clean backend architecture (FastAPI + SQLAlchemy + Alembic).
- Offer a usable analyst workflow: case lifecycle, timeline, IOC/artifact linkage, notes, reporting.

## MVP Features
- Case management: create, update, list, filter, close, reopen.
- Investigation timeline with analyst events.
- IOC management (IP, domain, URL, hash, CVE, email) with confidence/source/tags.
- Artifact tracking (paths, outputs, links, text evidence).
- Analyst notes with important flag.
- Report generation in Markdown, HTML, and JSON.
- Dark, responsive web UI with dashboard and case detail view.

## Architecture

```text
incidentdesk/
├── README.md
├── pyproject.toml
├── alembic.ini
├── alembic/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── db.py
│   ├── models.py
│   ├── schemas.py
│   ├── services/
│   ├── routers/
│   ├── templates/
│   ├── static/
│   └── utils/
├── tests/
└── .github/workflows/ci.yml
```

## Tech Stack
- Python 3.11+
- FastAPI
- SQLAlchemy 2.x
- Alembic
- SQLite (MVP)
- Jinja2 templates
- pytest, ruff, mypy

## Quickstart

```bash
cd incidentdesk
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
alembic upgrade head
uvicorn app.main:app --reload
```

Open: `http://127.0.0.1:8000`

## Web Usage
- Dashboard: `/`
- Cases list and create form: `/cases`
- Case detail + timeline/IOC/artifact/notes: `/cases/{case_id}`
- Report view: `/cases/{case_id}/report`
- Demo data loader (web button): `POST /demo/seed`

## Why the UI can be empty
- A fresh database starts with zero cases by design.
- Load realistic sample incidents from the dashboard or cases page via **Load Demo Dataset / Seed Demo Data**.
- Use **Reset + Reload Demo** when you want to replace existing data with a clean demo set.

## API Usage

### Cases
- `GET /api/cases`
- `POST /api/cases`
- `GET /api/cases/{case_id}`
- `PATCH /api/cases/{case_id}`
- `POST /api/cases/{case_id}/close`
- `POST /api/cases/{case_id}/reopen`

### Timeline
- `GET /api/cases/{case_id}/timeline`
- `POST /api/cases/{case_id}/timeline`

### IOC
- `GET /api/cases/{case_id}/iocs`
- `POST /api/cases/{case_id}/iocs`
- `PATCH /api/iocs/{ioc_id}`
- `DELETE /api/iocs/{ioc_id}`

### Artifacts
- `GET /api/cases/{case_id}/artifacts`
- `POST /api/cases/{case_id}/artifacts`
- `PATCH /api/artifacts/{artifact_id}`
- `DELETE /api/artifacts/{artifact_id}`

### Notes
- `GET /api/cases/{case_id}/notes`
- `POST /api/cases/{case_id}/notes`

### Reports
- `GET /api/cases/{case_id}/report.md`
- `GET /api/cases/{case_id}/report.html`
- `GET /api/cases/{case_id}/report.json`

## Tests and Quality

```bash
ruff check .
mypy app
pytest
```

CI (`.github/workflows/ci.yml`) runs lint + type checks + tests on push/PR.

## Screenshots
Store captures in `docs/screenshots/`.

## Roadmap
- Pagination and sorting for cases.
- Authentication/authorization (RBAC).
- Full-text IOC search improvements.
- Better report rendering templates/PDF export.
- Optional integrations (ticketing, threat intel feeds).

## Known Limits (MVP)
- SQLite only by default.
- No auth in MVP.
- No binary evidence upload pipeline.
- HTML report endpoint returns preformatted HTML from markdown text.

## Defensive / DFIR Scope
IncidentDesk is strictly defensive and investigation-focused:
- incident tracking
- evidence organization
- IOC correlation support
- reporting and remediation documentation

No offensive capabilities are included.
