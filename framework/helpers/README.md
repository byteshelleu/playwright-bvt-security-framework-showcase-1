# helpers

| Module | Purpose |
|---|---|
| `sign_in.py` | The only way a test signs in, one entry point per landing page |
| `session_cache.py` | One saved session per account, restored instead of a new login, under a per-account file lock |
| `seeder.py` | The one entry point for test data: refuse, register cleanup, create, return a record |
| `cleanup.py` | Removes what registered accounts own, matched by the data prefix |
| `api_client.py` | The API the seeder and the account fixtures create data through; never imported by a spec |
| `api_contracts.py` | Strict contracts for every API answer used to arrange data |
| `test_data.py` | Generated accounts, passwords, addresses and cards, all carrying the prefix |
| `records.py` | Typed records passed between the layers; secrets stay out of reprs |
| `display.py`, `text_patterns.py` | How the shop writes values; how locators match text |
