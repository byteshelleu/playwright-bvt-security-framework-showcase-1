# CLAUDE.md

Byte Shell's test automation showcase: a Playwright + pytest framework with a functional BVT suite and a security suite, run against OWASP Juice Shop. It is read by people we present our work to, so every file must make sense to a stranger.

## 0. Rules that hold on every task

| | Rule |
|---|---|
| MUST | Run the deny-list check before every commit: no deny-listed term in any tracked file, commit message, branch name or pull request. The list is private and never committed; CI reads it from the `DENYLIST` repository secret. |
| MUST | Run the secret scan before every commit; no credentials anywhere. |
| MUST | Write everything from scratch for this repository. Patterns may follow how we build frameworks; code, names, data and wording from other work may not. |
| MUST | Test only Juice Shop running locally (Docker) or as a CI service container, never a public or third-party instance. |
| MUST | Commit as the organisation's neutral author, with plain imperative messages and no AI attribution. Keep the history to one commit: amend it, then force-push. |
| MUST | Commit and push only on the owner's explicit approval. |
| MUST | Keep the rule checker clean: `uv run python -m tools.rules_checker` enforces the framework's rules by id; a justified exemption goes on its line as `# noqa: <RULE>`. |
| WON'T | Personal names, emails, product or company names other than Byte Shell, hosts, ids, or any description of another system's architecture. |
| WON'T | `time.sleep()`, `networkidle` waits, XPath outside the logged Tier 4 waiver, `expect()` or locators in a test, loops in a test, the same steps written twice, `#` comments. |

## 1. What the framework shows

- **Layers:** locator classes (role first, then test id), page objects with actions only, a sibling `*_page_assertions.py` with assertions only, a constants module per area, and tests whose docstrings list their numbered steps.
- **Data and sessions:** a factory generates the account fixtures; each fixture account logs in once per worker and its session is restored after that; tests sign in through entry points and seed through one seeder, which registers cleanup before it creates; cleanup matches the run's prefix.
- **Parallel runs:** xdist groups for tests that share state; every test still seeds what it needs and runs on its own.
- **CI:** GitHub Actions, one job per area run in order, a `cases` input that runs selected cases, retries for infrastructure errors only, per-area reports, and a merged dry-run case report.
- **Quality gates:** ruff, mypy strict, unit tests for the framework itself, and a rule checker with hooks.

## 2. The two suites

- **BVT:** registration and login, product search, basket, checkout, order history, account settings.
- **Security:** access to other customers' data (IDOR), endpoints missing authorization, login rate limiting, security headers, sensitive data in API responses, injection on login and search. A check fails plainly when the application is vulnerable; Juice Shop is vulnerable on purpose, so the security job is red by design. Security tests are never retried.

## 3. README for visitors

Say what the repository is and that Byte Shell built it. Say the patterns were first built for a multi-tenant K-12 education platform (education sector, B2B) with role-based access, data kept separate per customer, generated PDF documents, timezone-aware dates and email flows, where the original suites ran about 950 functional tests plus a security suite, by area, in CI. Then what this showcase demonstrates and how to run it in a few commands. Nothing else about the original platform.

## 4. Stack

Python 3.12, uv, pytest, Playwright (sync API, Chromium), pytest-xdist, pytest-rerunfailures, pytest-html, pydantic, filelock, ruff, mypy, Docker for Juice Shop.
