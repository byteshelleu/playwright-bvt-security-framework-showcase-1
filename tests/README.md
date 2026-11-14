# tests

| Path | Holds |
|---|---|
| `bvt/` | The build verification suite, one file per feature |
| `security/` | The security suite, one file per category |
| `unit/` | Unit tests for the framework and the tools; no browser, no shop |
| `conftest.py` | Hooks, session fixtures, and the registration of the account fixtures |
| `fixtures_factory.py` | Generates one `<label>_account` fixture per account label |
| `data_fixtures.py`, `page_fixtures.py` | API, cleanup and seeder fixtures; page objects, constructed only |

A test is its numbered steps: the docstring lists them with their expected
results, and the body follows them in blank-line groups.
