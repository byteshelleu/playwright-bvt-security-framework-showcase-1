# security

| Module | Holds |
|---|---|
| `client.py` | A thin client that never raises on a status, so each test reads it |
| `payloads.py` | Probe inputs, data only and never destructive |
| `probes.py` | Request bodies, probes of more than one request, and reading a token as an attacker would |
| `asserts.py` | `assert_*` functions whose messages name what was allowed or leaked |
| `security_constants.py` | Expected header values, secret field names, status codes |

Routes come from `framework/api_constants.py`, shared with the API client. A security
test checks the route is live before each negative probe, expects an exact status, fails
plainly when the shop is vulnerable, and is never retried.
