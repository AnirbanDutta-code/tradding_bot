#  imports 
import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode




class BinanceFuturesClient:
    
    # API credentials 
    
    def __init__(self, api_key: str, api_secret: str, base_url: str):
        self.api_key = api_key
        self.api_secret = api_secret.encode()
        self.base_url = base_url.rstrip("/")

    # Add Binance signature 
    def _sign(self, params: dict) -> dict:
        query_string = urlencode(params, True)
        signature = hmac.new(self.api_secret, query_string.encode(), hashlib.sha256).hexdigest()
        params["signature"] = signature
        return params

    # headers 
    def _headers(self) -> dict:
        return {
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded"
        }

    # Raise a clearer error message for Binance HTTP failures.
    def _raise_for_status(self, response: requests.Response) -> None:
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            try:
                error_payload = response.json()
                error_message = error_payload.get("msg") or str(error_payload)
            except ValueError:
                error_message = response.text.strip() or str(exc)
            raise requests.HTTPError(
                f"Binance API error ({response.status_code}): {error_message}",
                response=response,
            ) from exc

##================ authentication check ===============

    def check_auth(self) -> dict:
        endpoint = "/api/v3/account"
        url = self.base_url + endpoint
        params = {"timestamp": int(time.time() * 1000)}
        signed_params = self._sign(params)

        response = requests.get(url, headers=self._headers(), params=signed_params, timeout=10)
        self._raise_for_status(response)
        return response.json()

    # Submit a new order to Binance Spot
    
    def place_order(self, symbol: str, side: str, order_type: str,
                    quantity: float, price: float | None = None) -> dict:
        endpoint = "/api/v3/order"
        url = self.base_url + endpoint

        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
            "timestamp": int(time.time() * 1000)
        }

        if order_type == "LIMIT":
            params["price"] = price
            params["timeInForce"] = "GTC"

        signed_params = self._sign(params)

        response = requests.post(url, headers=self._headers(), data=signed_params, timeout=10)
        self._raise_for_status(response)
        return response.json()

    def check_availabe_symbols():
        endpoint = "/api/v3/exchangeInfo"
        url = self.base_url + endpoint
        params = {"timestamp": int(time.time() * 1000)}
        signed_params = self._sign(params)

        response = requests.get(url, headers=self._headers(), params=signed_params, timeout=10)
        self._raise_for_status(response)
        return response.json()