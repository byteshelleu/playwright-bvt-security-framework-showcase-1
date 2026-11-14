# pages

One page object per page, with its siblings:

- `*_page.py`: actions only. It holds the Playwright page and composes `self.loc` (its
  locators) and `self.assertions`; `navigate()` opens its route and waits through
  `assertions.loaded()`. Pages share no base class.
- `*_page_assertions.py`: assertions only, each named as the state it checks.
- `*_constants.py`: the names, messages and values the page uses.
