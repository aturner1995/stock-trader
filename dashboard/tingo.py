import requests

headers = {
        'Content-Type': 'application/json',
        'Authorization' : 'Token 9a49994b833d440273d685b24493ef5663a6f036'
        }

def get_meta_data(stock):
    url = 'https://api.tiingo.com/tiingo/daily/{}'.format(stock)
    response = requests.get(url, headers=headers)
    print(response.json())  # Add this line for debugging
    return response.json()