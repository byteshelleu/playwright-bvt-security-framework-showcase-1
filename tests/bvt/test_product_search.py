"""BVT: product search."""

from __future__ import annotations

import pytest

from framework.pages.catalogue_constants import BANANA_JUICE
from framework.pages.product_list_constants import MATCHING_SEARCH_TERM, UNMATCHED_SEARCH_TERM
from framework.pages.product_list_page import ProductListPage

pytestmark = pytest.mark.bvt


def test_search_finds_matching_product(product_list_page: ProductListPage) -> None:
    """BVT: Searching lists the matching product only.

    Steps and expected results:
    1. Open the product list and search for "banana" -> the results name the term.
    2. Read the results -> Banana Juice is the one product listed, with its price.
    """
    product_list_page.navigate()
    product_list_page.navbar.search_for(MATCHING_SEARCH_TERM)
    product_list_page.assertions.results_for(MATCHING_SEARCH_TERM)

    product_list_page.assertions.shows_only(BANANA_JUICE)


def test_search_without_matches_lists_nothing(product_list_page: ProductListPage) -> None:
    """BVT: Searching for a term no product holds lists nothing.

    Steps and expected results:
    1. Open the product list and search for a term no product holds -> the results name the term.
    2. Read the results -> no product is listed.
    """
    product_list_page.navigate()
    product_list_page.navbar.search_for(UNMATCHED_SEARCH_TERM)
    product_list_page.assertions.results_for(UNMATCHED_SEARCH_TERM)

    product_list_page.assertions.shows_no_products()
