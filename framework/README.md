# framework

The code tests are written against. Each layer has one job:

| Folder | Holds |
|---|---|
| `locators/` | Where elements are: one class per page, a `@property` or a factory per element |
| `pages/` | What a user does on a page (`*_page.py`), what must be true (`*_page_assertions.py`), and the values both use (`*_constants.py`) |
| `components/` | The same split for parts shown on many pages, such as the top bar |
| `helpers/` | Sign-in, saved sessions, the seeder, the API it seeds through, test data |
| `security/` | The security suite's client, probes, payloads and assertions |
| `reporting/` | Case mapping, case selection and the retry report |

`config.py` resolves where the shop runs and refuses any host but this machine.
`constants.py` holds the values shared across layers, `api_constants.py` the API routes,
`test_data_constants.py` the values generated data is built from, and `ci_constants.py` the
CI areas and xdist groups.
