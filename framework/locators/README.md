# locators

The only place an element is located. Each class takes the page and exposes a
`@property` per static element and a factory method per element found by data
(a product name, a street). Names come from the page's constants module.

Order of preference: role, then test id. Juice Shop has no `data-testid`, so the
test id is its `id` attribute. Anything else is a TIER 4 locator, marked in its
docstring and listed in `docs/locators-tracker.md` with what the shop would need.
