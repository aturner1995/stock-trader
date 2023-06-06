import requests
from dotenv import load_dotenv, dotenv_values

load_dotenv()  # take environment variables from .env.

config = dotenv_values(".env")

def get_stock_data(stock):
    url = "https://data.alpaca.markets/v2/stocks/{}/bars?timeframe=5Min&limit=1000&adjustment=raw".format(stock)

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
        for bar in data["bars"]:
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