from decimal import Decimal

import pytest

from app.pricing import discount_for, subtotal, total


def test_subtotal_sums_price_times_qty():
    assert subtotal([(100, 2), (50.5, 1)]) == Decimal("250.50")


def test_subtotal_rejects_negative_quantity():
    with pytest.raises(ValueError):
        subtotal([(100, -1)])


@pytest.mark.parametrize("amount,rate", [
    (Decimal("1999.99"), Decimal("0")),
    (Decimal("2000"), Decimal("0.05")),
    (Decimal("4999.99"), Decimal("0.05")),
    (Decimal("5000"), Decimal("0.10")),
])
def test_discount_tiers(amount, rate):
    assert discount_for(amount) == rate


def test_total_applies_discount_then_tax():
    result = total([(2500, 1)])
    assert result["subtotal"] == Decimal("2500.00")
    assert result["discount"] == Decimal("125.00")        # 5% of 2500
    assert result["tax"] == Decimal("427.50")             # 18% of 2375
    assert result["total"] == Decimal("2802.50")


def test_total_with_no_items_is_zero():
    assert total([])["total"] == Decimal("0.00")
