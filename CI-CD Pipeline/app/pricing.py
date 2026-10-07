"""Order pricing rules for a small shop. Pure functions, easy to unit test."""

from decimal import ROUND_HALF_UP, Decimal

TAX_RATE = Decimal("0.18")

DISCOUNT_TIERS = (
    # (minimum subtotal, discount fraction)
    (Decimal("5000"), Decimal("0.10")),
    (Decimal("2000"), Decimal("0.05")),
)


def _money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def subtotal(items):
    """items: iterable of (unit_price, quantity). Rejects negative values."""
    total = Decimal("0")
    for price, qty in items:
        price, qty = Decimal(str(price)), int(qty)
        if price < 0 or qty < 0:
            raise ValueError("price and quantity must be non-negative")
        total += price * qty
    return _money(total)


def discount_for(amount: Decimal) -> Decimal:
    for threshold, rate in DISCOUNT_TIERS:
        if amount >= threshold:
            return rate
    return Decimal("0")


def total(items):
    """Subtotal, minus tiered discount, plus tax. Returns a dict of the parts."""
    sub = subtotal(items)
    disc = _money(sub * discount_for(sub))
    taxable = sub - disc
    tax = _money(taxable * TAX_RATE)
    return {
        "subtotal": sub,
        "discount": disc,
        "tax": tax,
        "total": _money(taxable + tax),
    }
