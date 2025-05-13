import requests
import pandas as pd
import yfinance as yf

ALPHA_API_KEY = 'W5EXBDLHMG8TRB7M'
ALPHA_BASE_URL = 'https://www.alphavantage.co/query'

def fetch_data(symbol, source, interval='60min'):
    if source == "yf":
        print("Using yfinance")
        return fetch_data_yf(symbol)
    elif source == "al":
        print("Using Alpha Vantage")
        return fetch_data_alpha(symbol, interval)
    else:
        raise ValueError("Invalid source. Use 'yf' for yfinance or 'al' for Alpha Vantage.")



def fetch_data_alpha(symbol, interval):
    params = {
        'function': 'TIME_SERIES_INTRADAY',
        'symbol': symbol,
        'interval': interval,
        'apikey': ALPHA_API_KEY,
        'outputsize': 'full'
    }
    response = requests.get(ALPHA_BASE_URL, params=params, timeout=10)
    if response.status_code != 200:
        raise RuntimeError(f"Alpha Vantage API error: {response.status_code}")

    data = response.json()
    key = f"Time Series ({interval})"
    if key not in data:
        raise ValueError(f"Unexpected Alpha Vantage response: {data}")

    df = pd.DataFrame.from_dict(data[key], orient='index', dtype=float)
    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    df.index = df.index.tz_localize('America/New_York')
    return df

def fetch_data_yf(symbol, interval="60m"):
    df = yf.download(symbol, period="60d", interval=interval, progress=False)
    if df.empty:
        raise ValueError(f"yfinance returned no data for {symbol}")
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC").tz_convert("America/New_York")
    else:
        df.index = df.index.tz_convert("America/New_York")
    return df
