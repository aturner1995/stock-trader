import requests
from dotenv import load_dotenv, dotenv_values
from datetime import datetime, timedelta

load_dotenv()  # take environment variables from .env.

config = dotenv_values(".env")

def get_stock_data(stock, time_period):
    # If else statement to check the time period and 
    if time_period == '1D':
        timeframe = '5Min'
        start = datetime.now()
    elif time_period == '1W':
        timeframe = '30Min'
        start = datetime.now()-timedelta(days=7)
    elif time_period == '1M':
        timeframe = '1D'
        start = datetime.now()-timedelta(days=30)
    elif time_period == '1Y':
        timeframe = '1D'
        start = datetime.now()-timedelta(days=365)
    else:
        return [], []

    formatted_start = start.strftime('%Y-%m-%d')    
    url = "https://data.alpaca.markets/v2/stocks/bars?symbols={}&start={}&timeframe={}&limit=1000&adjustment=raw".format(stock, formatted_start, timeframe)
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": config['APCA-API-KEY-ID'],
        "APCA-API-SECRET-KEY": config['APCA-API-SECRET-KEY']
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    close_prices = []
    timestamps = []
    if "bars" in data:
        stock_data = data["bars"].get(stock)  # Get the list of bars for the given stock symbol
        if stock_data:
            for bar in stock_data:
                if "c" in bar:
                    close_prices.append(bar["c"])
                    timestamps.append(bar["t"])

    return close_prices, timestamps


def get_stock_news(stock):
    url = "https://data.alpaca.markets/v1beta1/news?symbols={}".format(stock)
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": config['APCA-API-KEY-ID'],
        "APCA-API-SECRET-KEY": config['APCA-API-SECRET-KEY']
    }
    response = requests.get(url, headers=headers)
    return response.json()
