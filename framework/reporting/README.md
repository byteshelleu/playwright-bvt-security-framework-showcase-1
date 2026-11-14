# reporting

- `cases.py`: the test-to-case mapping read from `config/test_cases.toml`, and the
  case reporter interface with its dry-run adapter.
- `plugin.py`: `--area` and `--cases` select tests; `--flaky-report` lists tests that
  passed only after an infrastructure retry.
