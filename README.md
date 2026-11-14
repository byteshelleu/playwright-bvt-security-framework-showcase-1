# Playwright BVT and security test framework

A test automation framework built by **Byte Shell**, shown here running two suites against
[OWASP Juice Shop](https://owasp.org/www-project-juice-shop/): a functional build verification
test (BVT) suite and a security suite. It uses Python, pytest and Playwright.

## Where the patterns come from

We first built these patterns for a multi-tenant K-12 education platform (education sector,
B2B). That product has role-based access, data kept separate per customer, generated PDF
documents, timezone-aware dates and email flows. Its suites ran about 950 functional tests plus
a security suite, by area, in CI.

This repository rebuilds the same patterns from scratch against Juice Shop, an application made
to be tested in the open.

## What it demonstrates

**Layers.** Each page has a locator class and three sibling modules:

| Module | Holds | Example |
|---|---|---|
| `framework/locators/basket_locators.py` | Where elements are: role first, then test id | `checkout_button` |
| `framework/pages/basket_page.py` | What a user does: actions only | `remove(product)` |
| `framework/pages/basket_page_assertions.py` | What must be true: assertions only | `is_empty()` |
| `framework/pages/basket_constants.py` | The names and values both use | `CHECKOUT_NAME` |

A page object holds its locators as `self.loc` and its assertions as `self.assertions`.
A test is its numbered steps: the docstring lists them with their expected results, and the
body follows them.

```python
def test_basket_remove_leaves_empty(page: Page, shopper: Account, seeder: Seeder) -> None:
    """BVT: Removing the only product empties the basket.

    Steps and expected results:
    1. With Apple Juice in the basket, sign in and open the basket -> it is listed.
    2. Remove it -> no line is left and checkout is not offered.
    """
    seeder.basket(shopper, APPLE_JUICE)
    basket = sign_in_to_basket(page, shopper)

    basket.remove(APPLE_JUICE)
    basket.assertions.is_empty()
```

Juice Shop gives some elements neither a role nor a test id. Each locator that works around
that is listed in [`docs/locators-tracker.md`](docs/locators-tracker.md), with what the shop
would need for it to become a role locator.

**Accounts, sessions and data.**

- A fixture factory generates one fixture per account, with passwords created per run.
- A fixture account logs in once per worker. Its session is saved under a per-account file
  lock, and every later sign-in restores it
  ([`framework/helpers/session_cache.py`](framework/helpers/session_cache.py)). An account a test
  creates for itself logs in through the login page and is never saved.
- A test signs in only through the entry points in
  [`framework/helpers/sign_in.py`](framework/helpers/sign_in.py). Each returns the page it lands on.
- Test data is seeded only through the seeder
  ([`framework/helpers/seeder.py`](framework/helpers/seeder.py)). Every seeding method registers
  its cleanup before it creates anything, and the cleanup removes only records that carry the
  run's prefix.
- Every API answer used to create data is checked against a strict contract, so a backend
  change fails where the data is created.

**Parallel runs.** Tests run on several pytest-xdist workers with `--dist loadgroup`. Tests
that share state, such as the basket cases on one shopper account, are in one xdist group, so
they never run at once. Each still seeds what it needs, so any test can run on its own.

**The security suite** covers:

- access to other customers' baskets, addresses, cards and orders;
- endpoints missing authorization;
- login rate limiting;
- security headers;
- sensitive data in API responses;
- injection on login and search.

Each check states what a secure application must do and fails when the application does not.
Before every negative probe, the test checks the route answers normally, so a refusal is a real
refusal, and a refusal must carry exactly the expected status. Juice Shop is insecure on purpose, so several security tests fail and the security job
is red by design. Failures are written to a findings file, and security tests are never retried.

**CI** ([`.github/workflows`](.github/workflows)):

- A quality gate on every push to `main` and every pull request: ruff, mypy, the rule checker
  and the unit tests.
- The suites run in three areas (account, shopping, security), one job after another. An area
  runs even when the one before it failed.
- The `Cases` input on a manual run takes case names from
  [`config/test_cases.toml`](config/test_cases.toml). Only the areas that hold those cases run,
  and an unknown name stops the run before any area starts.
- A test is retried only for an infrastructure error (a dropped connection, a closed browser),
  never for a wrong result, and security tests never. A run is retried only when pytest itself
  broke. Every test that passed only after a retry is listed in the job summary.
- Each area uploads its JUnit file, HTML report, and screenshots and traces of failures.

**Case management, dry run.** Tests never name a test case; the mapping lives in config. A final
CI job merges every area's results into one report and passes it to a reporter interface. The
only adapter included is a dry run: it writes the request it would send as a CI artifact.

**Quality gates**, run in pre-commit hooks and in CI:

- ruff and mypy in strict mode;
- unit tests for the framework and its tools;
- a rule checker ([`tools/rules_checker.py`](tools/rules_checker.py)) that blocks:
  - fixed sleeps, `networkidle` waits and XPath outside the documented exceptions;
  - `expect()`, locators, loops or module-level values in a test;
  - the same six steps written twice;
  - assertions or actions in the wrong layer;
  - inline values where a named constant belongs;
  - `#` comments;
  - CI settings that would retry a wrong result;
- a secret scan and a deny-list check.

## Run it

You need Docker and [uv](https://docs.astral.sh/uv/).

```bash
docker compose up -d --wait                 # Juice Shop on 127.0.0.1:3000
uv sync && uv run playwright install chromium
uv run pytest tests/bvt tests/security -n 4 --dist loadgroup
```

Run one area, or selected cases:

```bash
uv run pytest tests --area shopping -n 4 --dist loadgroup
uv run pytest tests --cases "bvt.basket.add-product, security.idor.basket-read"
```

The suites only run against a Juice Shop on this machine. Any other host is refused before a
request is sent ([`framework/config.py`](framework/config.py)).

To work on the framework, install [gitleaks](https://github.com/gitleaks/gitleaks), then
install the hooks once:

```bash
uv run pre-commit install
```

Stop Juice Shop with `docker compose down`. It starts with fresh data every time.
