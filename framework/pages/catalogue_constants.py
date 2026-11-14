"""Products and delivery methods from Juice Shop's own seed data."""

from __future__ import annotations

from framework.helpers.records import DeliveryMethod, Product

APPLE_JUICE: Product = Product(id=1, name="Apple Juice (1000ml)", price=1.99)
BANANA_JUICE: Product = Product(id=6, name="Banana Juice (1000ml)", price=1.99)
ONE_DAY_DELIVERY: DeliveryMethod = DeliveryMethod(id=1, name="One Day Delivery", price=0.99)
STANDARD_DELIVERY: DeliveryMethod = DeliveryMethod(id=3, name="Standard Delivery", price=0.0)
