# Locators tracker

Every locator that is not Tier 1 (role) or Tier 2 (test id) is listed here, with
what the application would need for it to become Tier 1. The rule checker (L010)
fails a TIER 3, TIER 4 or BLOCKER locator that has no row.

Tier 2 reads the `id` attribute: Juice Shop has no `data-testid`, and its ids
are the stable hooks it gives its own tests.

| Locator | File | Tier | Why | What would make it Tier 1 |
|---|---|---|---|---|
| `increase_button` | `framework/locators/basket_locators.py` | 4 | The + button has no accessible name | An `aria-label` such as "Increase quantity" |
| `decrease_button` | `framework/locators/basket_locators.py` | 4 | The - button has no accessible name | An `aria-label` such as "Decrease quantity" |
| `remove_button` | `framework/locators/basket_locators.py` | 4 | The delete button has no accessible name | An `aria-label` such as "Remove from basket" |
| `order_cards` | `framework/locators/order_history_locators.py` | 4 | An order card has no role or test id | `role="article"` and a name on each order card |
