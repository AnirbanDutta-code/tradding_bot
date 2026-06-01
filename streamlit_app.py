# ====================== Streamlit UI ===============================
import os
import streamlit as st
from dotenv.main import load_dotenv   
from bot.client import BinanceFuturesClient
from bot.orders import place_order
from bot.validators import validate_order_input


# ====================== trimming spaces  ======================

def clean_env_value(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in {'"', "'"}:
        cleaned = cleaned[1:-1].strip()
    return cleaned


#====================== Load  envs ======================

def load_env_config() -> tuple[str, str, str]:
    load_dotenv()

    # ======= store check envs ==========

    api_key = clean_env_value(os.getenv("API_KEY"))
    api_secret = clean_env_value(os.getenv("API_SECRET"))
    base_url = clean_env_value(os.getenv("BASE_URL"))

    credentials = {
        "API_KEY": api_key,
        "API_SECRET": api_secret,
        "BASE_URL": base_url,
    }
    missing_vars = [name for name, value in credentials.items() if not value]
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    return api_key, api_secret, base_url


# ====================== UI ======================w.
def main() -> None:
    st.set_page_config(page_title="Trading Bot", page_icon="📈", layout="centered")
    st.title("Trading Bot ( Binance Testnet)")

    try:
        api_key, api_secret, base_url = load_env_config()
    except ValueError as env_error:
        st.error(str(env_error))
        st.info("Update .env  then restart.")
        return

    with st.form("place_order_form"):
        symbol = st.text_input("Symbol", value="BTCUSDT").strip().upper()
        side = st.selectbox("Side", options=["BUY", "SELL"])
        order_type = st.selectbox("Order Type", options=["MARKET", "LIMIT"])
        quantity = st.number_input("Quantity", min_value=0.0, step=0.001, format="%.6f")

        price = None
        if order_type == "LIMIT":
            price = st.number_input("Price", min_value=0.0, step=0.01, format="%.6f")

        submitted = st.form_submit_button("Place Order")

    if not submitted:
        return

    try:
        validate_order_input(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
        )
    except ValueError as validation_error:
        st.error(f"Validation error: {validation_error}")
        return

    client = BinanceFuturesClient(api_key, api_secret, base_url)

    with st.spinner("placing order..."):
        try:
            response = place_order(
                client=client,
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                logger=None,
            )
        except Exception as order_error:
            st.error(f"Order failed: {order_error}")
            return


    st.success("order placed succesfully")
    
    st.info("order summery")
    st.json(
        {
            "orderId": response.get("orderId"),
            "status": response.get("status"),
            "executedQty": response.get("executedQty"),
            "avgPrice": response.get("avgPrice"),
            "raw": response,
        }

    )


if __name__ == "__main__":
    main()
