# Contributing to IncidentDesk

Thanks for contributing.

## Development Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
alembic upgrade head
```

## Project Standards
- Keep scope defensive and DFIR-focused.
- Prefer small, focused pull requests.
- Add/adjust tests for behavior changes.
- Keep code quality green before opening PR:

```bash
ruff check .
mypy app
pytest
```

## Commit Style
Use clear, conventional commit messages when possible, for example:
- `feat: add IOC search filter`
- `fix: handle case reopen timestamp`
- `docs: improve API examples`

## Pull Request Checklist
- [ ] Tests updated or added
- [ ] Lint and mypy pass
- [ ] README/docs updated if behavior changed
- [ ] No personal/sensitive data included
