# imports 
from .client import BinanceFuturesClient
from .validators import validate_order_input


# Validate inputs, place the order, and log request/response lifecycle.
def place_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None = None,
    logger=None,
) -> dict:
    validate_order_input(symbol, side, order_type, quantity, price)

    if logger:
        logger.info(
            f"REQUEST | symbol={symbol} side={side} type={order_type} "
            f"quantity={quantity} price={price}"
        )

    try:
        response = client.place_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
        )

        if logger:
            logger.info(f"RESPONSE | {response}")

        return response

    except Exception as e:
        if logger:
            logger.error(f"ERROR | {str(e)}")
        raise