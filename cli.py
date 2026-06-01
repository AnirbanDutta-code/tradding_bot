# Standard library imports for argument parsing and environment access.

import argparse
import os
import sys
from dotenv import load_dotenv

# Local modules
from bot.client import BinanceFuturesClient
from bot.orders import place_order
from bot.logging_config import setup_logging
from bot.validators import validate_order_input


# Normalize environment values by trimming spaces and optional wrapping quotes.
def _clean_env_value(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in {'"', "'"}:
        cleaned = cleaned[1:-1].strip()
    return cleaned


# Prompt until user enters one of the allowed values.
def _prompt_menu(label: str, options: list[str]) -> str:
    option_text = " / ".join(options)
    while True:
        value = input(f"{label} ({option_text}): ").strip().upper()
        if value in options:
            return value
        print(f"Invalid choice. Please pick one of: {option_text}")


# Prompt until user provides a valid positive float.
def _prompt_positive_float(label: str) -> float:
    while True:
        value = input(f"{label}: ").strip()
        try:
            number = float(value)
        except ValueError:
            print("Invalid number. Please enter a numeric value.")
            continue
        if number <= 0:
            print("Value must be greater than 0.")
            continue
        return number


# Prompt until user provides a non-empty trading symbol.
def _prompt_symbol() -> str:
    while True:
        symbol = input("Symbol (e.g., BTCUSDT): ").strip().upper()
        if symbol:
            return symbol
        print("Symbol cannot be empty.")


# Build final order inputs using args first, then interactive prompts for missing values.
def _collect_order_inputs(args: argparse.Namespace) -> tuple[str, str, str, float, float | None]:
    
    symbol = args.symbol.strip().upper() if args.symbol else _prompt_symbol()
    side = args.side.upper() if args.side else _prompt_menu("Side", ["BUY", "SELL"])
    order_type = args.type.upper() if args.type else _prompt_menu("Order type", ["MARKET", "LIMIT"])
    quantity = args.quantity if args.quantity is not None else _prompt_positive_float("Quantity")

    price = args.price
    if order_type == "LIMIT" and price is None:
        price = _prompt_positive_float("Price")

    return symbol, side, order_type, quantity, price


# Validate required .env keys and return values.
def _load_env_config() -> tuple[str, str, str]:
    load_dotenv()

    api_key = _clean_env_value(os.getenv("API_KEY"))
    api_secret = _clean_env_value(os.getenv("API_SECRET"))
    base_url = _clean_env_value(os.getenv("BASE_URL"))

    required_vars = {
        "API_KEY": api_key,
        "API_SECRET": api_secret,
        "BASE_URL": base_url,
    }
    missing_vars = [name for name, value in required_vars.items() if not value]
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    return api_key, api_secret, base_url


# Main command-line entry point for placing an order.
def main():
    parser = argparse.ArgumentParser(description="Binance Spot Testnet Trading Bot")

    parser.add_argument(
        "--check-auth",
        action="store_true",
        help="Validate API key/secret permissions without placing an order",
    )
    parser.add_argument("--symbol")
    parser.add_argument("--side", choices=["BUY", "SELL"])
    parser.add_argument("--type", choices=["MARKET", "LIMIT"])
    parser.add_argument("--quantity", type=float)
    parser.add_argument("--price", type=float)

    args = parser.parse_args()

    logger = setup_logging()

    try:
        api_key, api_secret, base_url = _load_env_config()
        client = BinanceFuturesClient(api_key, api_secret, base_url)

        if args.check_auth:
            account_info = client.check_auth()
            print("\n=== AUTH CHECK SUCCESS ===")
            print(f"Can Trade: {account_info.get('canTrade')}")
            print(f"Can Deposit: {account_info.get('canDeposit')}")
            print(f"Can Withdraw: {account_info.get('canWithdraw')}")
            return

        symbol, side, order_type, quantity, price = _collect_order_inputs(args)

        try:
            validate_order_input(symbol, side, order_type, quantity, price)
        except ValueError as validation_error:
            print("\n=== INPUT VALIDATION ERROR ===")
            print(str(validation_error))
            sys.exit(1)

        print("\n=== ORDER PREVIEW ===")
        print(f"Symbol: {symbol}")
        print(f"Side: {side}")
        print(f"Type: {order_type}")
        print(f"Quantity: {quantity}")
        if price is not None:
            print(f"Price: {price}")

        confirm = input("Place this order? (y/n): ").strip().lower()
        if confirm not in {"y", "yes"}:
            print("Order cancelled.")
            return

        response = place_order(
            client=client,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            logger=logger,
        )

        print("\n=== ORDER SUCCESS ===")
        print(f"Order ID: {response.get('orderId')}")
        print(f"Status: {response.get('status')}")
        print(f"Executed Qty: {response.get('executedQty')}")
        print(f"Avg Price: {response.get('avgPrice')}")

    except Exception as e:
        print("\n=== ORDER FAILED ===")
        print(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()