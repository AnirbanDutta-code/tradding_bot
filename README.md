# Trading Bot (Brief)

## Setup Steps
1. Create and activate a Python virtual environment.
2. Install dependencies:
	 - `pip install -r requirements.txt`
3. Create/update `.env` in the project root with:
	 - `API_KEY=`
	 - `API_SECRET=`
	 - `BASE_URL=`

## How to Run (Examples)
- CLI (interactive prompts):
	- `python cli.py`

- CLI (fully via flags):
	- `python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01`
	- `python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 50000`

- Streamlit UI:
	- `streamlit run streamlit_app.py`

## Assumptions
- Python 3.10+ is installed.
- .env contains valid Binance credentials and base URL.
- You run commands from the tradding_bot root folder.
- Internet access is available for Binance API calls.
