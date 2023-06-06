import requests

def get_stock_data(stock):
    url = "https://data.alpaca.markets/v2/stocks/{}/bars?timeframe=5Min&limit=1000&adjustment=raw".format(stock)

    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": "PKMIRN2CCOR5LOL642E7",
        "APCA-API-SECRET-KEY": "A2G7mc3coS6En6REhqrVo9DxYQCcrz91vqGm4jha"
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
        print(close_prices ,timestamps)
    return close_prices, timestamps
