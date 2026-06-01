# Validation

def validate_order_input(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None = None,
) -> None:
    if not symbol or not symbol.isupper():
        raise ValueError("Symbol must be uppercase (e.g., BTCUSDT)")

    if side not in {"BUY", "SELL"}:
        raise ValueError("Side must be BUY or SELL")

    if order_type not in {"MARKET", "LIMIT"}:
        raise ValueError("Order type must be MARKET or LIMIT")

    if quantity <= 0:
        raise ValueError("Quantity must be greater than 0")

    if order_type == "LIMIT":
        if price is None:
            raise ValueError("Price is required for LIMIT orders")
        if price <= 0:
            raise ValueError("Price must be greater than 0")