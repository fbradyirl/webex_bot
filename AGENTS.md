# Agent Guidelines for webex_bot

Instructions for AI coding agents (Claude, Codex, Copilot, etc.) working on this repository.

## Project Overview

A Python library that lets developers create Webex messaging bots using WebSockets (no public IP or webhooks required). Users define `Command` subclasses and register them with a `WebexBot` instance.

- **Package**: `webex_bot` (published to PyPI)
- **Python**: 3.10+
- **Key dependency**: `webexpythonsdk` (not the older `webexteamssdk`)

## Repository Layout

```
webex_bot/          # Main package source
  webex_bot.py      # Core bot logic (WebexBot class)
  websockets/       # WebSocket client
  models/           # Command and Response models
  commands/         # Built-in commands (echo, help)
tests/              # All tests (pytest)
  conftest.py       # Shared fixtures and fakes
setup.py            # Package metadata and version
setup.cfg           # bumpversion config and pytest options
tox.ini             # Test environments and flake8
```

## Versioning

The version string lives in **three** files and must stay in sync:

1. `setup.py` — `version='X.Y.Z'`
2. `setup.cfg` — `current_version = X.Y.Z`
3. `webex_bot/__init__.py` — `__version__ = 'X.Y.Z'`

When bumping a version, update all three. The `setup.cfg` contains bumpversion configuration but manual updates are fine.

## Changelog

The changelog lives in `README.md` under the `# History` section. When making a release:

- Add a new `### X.Y.Z (YYYY-Mon-DD)` entry above the previous release.
- Reference GitHub issues/PRs with markdown link refs (e.g., `[#99][i99]`).
- Add the corresponding link reference at the bottom of the file (e.g., `[i99]: https://github.com/fbradyirl/webex_bot/issues/99`).

## Testing

### Running tests

```bash
# Full suite via tox (linting + tests across Python versions)
tox

# Direct pytest (faster for local iteration)
python -m pytest tests/ -v
```

### Test requirements

- Tests use **pytest** with **pytest-cov**. Coverage is configured in `setup.cfg` with an 80% minimum threshold.
- Flake8 max line length is **160** characters.
- Dev dependencies are pinned in `requirements_dev.txt`.

### Test conventions

- Tests live in `tests/` and follow `test_<module>.py` naming.
- Shared fixtures and fakes are in `tests/conftest.py`. The `bot` fixture monkeypatches the WebSocket client to avoid real network calls. Use the existing `DummyTeams`, `DummyMessages`, and `make_activity` helpers.
- Use `types.SimpleNamespace` to simulate SDK objects (messages, attachment actions).

### When to write tests

- **Bug fixes must include a regression test.** Reproduce the bug scenario in a test before or alongside the fix.
- **New commands or features** should have corresponding test cases covering the happy path and edge cases (e.g., `None` inputs, empty strings, missing keys).
- **Refactors** should not reduce coverage. Run `pytest --cov` to verify.

## Code Style and Quality

- Follow **PEP 8** with a max line length of **160**.
- Use `flake8` for linting (run via `tox` or standalone).
- Use Python's `logging` module — never `print()`. The project uses `coloredlogs`.
- Prefer f-strings for log messages and string formatting.

## Security

- **Never hardcode tokens, secrets, or credentials.** Bot tokens are passed at runtime via constructor args or environment variables (`WEBEX_ACCESS_TOKEN`).
- **Validate inputs from external sources.** WebSocket messages and card action payloads can contain `None` or missing fields — always guard against `None`/missing keys before calling methods like `.lower()`, `.get()`, etc.
- **Do not log sensitive data.** Never log full tokens, user credentials, or PII. Log only emails and non-sensitive identifiers at appropriate levels.

## Defensive Coding Practices

- Guard against `None` at trust boundaries — especially in `process_raw_command`, `process_incoming_card_action`, and `process_incoming_message` where SDK payloads may have missing fields.
- Prefer `dict.get()` with defaults over direct key access for activity/inputs dicts.
- When adding new parameters to public methods, provide sensible defaults to maintain backward compatibility.

## CI/CD

- GitHub Actions runs on push to `main` and on PRs (`.github/workflows/main.yml`).
- Tests run against Python 3.10, 3.11, and 3.12 via tox.
- Releases to PyPI are triggered automatically when a `v*` tag is pushed.
- A GitHub Release with auto-generated changelog is created by `.github/workflows/release.yml`.

## Release Checklist

1. Update version in `setup.py`, `setup.cfg`, and `webex_bot/__init__.py`.
2. Add changelog entry in `README.md`.
3. Commit, tag (`git tag -a vX.Y.Z -m "vX.Y.Z - description"`), and push.
4. CI publishes to PyPI and creates a GitHub Release automatically.
