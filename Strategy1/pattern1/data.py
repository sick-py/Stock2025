# data.py
# We use different library to fetch hourly stock data 
# The fetch_data function retrieves the hourly OHLCV (Open, High, Low, Close, Volume) data for a given stock symbol and date range. 
# We also include a get_stock_metadata function to fetch basic company info (like sector and industry), 
# which could be used in extended logic (though our pattern doesn’t utilize it yet).

import yfinance as yf
import pandas as pd
import requests


#Alpha
ALPHA_VANTAGE_API_KEY = "W5EXBDLHMG8TRB7M"  # Replace with your key
BASE_URL = "https://www.alphavantage.co/query"

# Function to fetch Alpha Vantage hourly data (60min intervals)
# in this API one we only get this month
def fetch_data_Alpha(symbol, interval="60min"):
    """
    Fetches intraday stock data (60-minute intervals) from Alpha Vantage.
    
    Args:
        symbol (str): Stock ticker (e.g., "AAPL")
        interval (str): Time interval ("60min" recommended)

    Returns:
        pd.DataFrame: DataFrame with datetime index and OHLCV columns
    """
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": interval,
        "apikey": ALPHA_VANTAGE_API_KEY,
        "outputsize": "full",
        "datatype": "json"
    }

    print(f"Requesting Alpha Vantage data for {symbol}...")
    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        raise RuntimeError(f"Request failed: {response.status_code} — {response.text}")

    data = response.json()
    key = f"Time Series ({interval})"
    if key not in data:
        raise ValueError(f"Unexpected response format: {data}")

    df = pd.DataFrame.from_dict(data[key], orient="index")
    df.columns = ["Open", "High", "Low", "Close", "Volume"]
    df = df.astype(float)
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    df.index = df.index.tz_localize("America/New_York")

    return df[["Open", "High", "Low", "Close", "Volume"]]

def fetch_data_Alpha_0(symbol, start_date, end_date, interval="60min"):
    print("use alpha to get data start")
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": interval,
        "apikey": ALPHA_VANTAGE_API_KEY,
        "outputsize": "full",
        "datatype": "json"
    }

    
    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch data for {symbol}: {response.status_code} {response.text}")

    print("use alpha to get data done")
    data = response.json()
    key = f"Time Series ({interval})"
    if key not in data:
        raise ValueError(f"Unexpected response for {symbol}: {data}")

    df = pd.DataFrame.from_dict(data[key], orient="index")
    df.columns = ["Open", "High", "Low", "Close", "Volume"]
    df = df.astype(float)
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    df.index = df.index.tz_localize("America/New_York")
    return df[["Open", "High", "Low", "Close", "Volume"]]













# IEX Cloud setup
IEX_TOKEN = "YOUR_IEX_CLOUD_SECRET_TOKEN"  # Replace with your token
BASE_URL = "https://cloud.iexapis.com/stable"

# Function to fetch IEX Cloud intraday data (1-hour intervals)
def fetch_data_iex(symbol, start_date, end_date, interval="1h"):
    url = f"{BASE_URL}/stock/{symbol}/chart/3m?token={IEX_TOKEN}&chartInterval=60"
    r = requests.get(url)
    if r.status_code != 200:
        raise ValueError(f"Failed to fetch data for {symbol}: {r.status_code} {r.text}")
    data = r.json()
    if not data:
        raise ValueError(f"No data returned for {symbol}")

    df = pd.DataFrame(data)
    df = df.rename(columns={
        "date": "Date",
        "minute": "Minute",
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume"
    })
    df["datetime"] = pd.to_datetime(df["Date"] + " " + df["Minute"])
    df.set_index("datetime", inplace=True)
    df = df[["Open", "High", "Low", "Close", "Volume"]]
    df.index = df.index.tz_localize("America/New_York")
    return df


def fetch_data_yf(symbol: str, start_date: str, end_date: str, interval: str = "1h") -> pd.DataFrame:
    df = yf.download(symbol, start=start_date, end=end_date, interval=interval)
    if df.empty:
        raise ValueError(f"No data returned for {symbol}. Check ticker or network.")
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC").tz_convert("America/New_York")
    else:
        df.index = df.index.tz_convert("America/New_York")

    return df


def get_stock_metadata_yf(symbol: str) -> dict:
    """
    Retrieves basic metadata for the given stock (e.g., sector, industry).
    :param symbol: Stock ticker symbol.
    :return: Dictionary with metadata like {'sector': ..., 'industry': ...}.
    """
    ticker = yf.Ticker(symbol)
    info = ticker.info
    return {
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "long_name": info.get("longName"),
    }
