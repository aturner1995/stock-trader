from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import StockForm
from .fetchData import get_stock_data, get_stock_news
import plotly.graph_objs as go
import plotly.io as pio

def index(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.cleaned_data['stock']
            return HttpResponseRedirect(stock)
    else:
        form = StockForm()
    
    return render(request, 'index.html', {'form': form})


def stock(request, id):
    context = {}
    context['stock'] = id

    form = StockForm(request.POST or None)
    if form.is_valid():
        time_period = form.cleaned_data['time_period']
        close_prices, timestamps = get_stock_data(id, time_period)
    else:
        close_prices, timestamps = get_stock_data(id, '1D')  # Default time period is 1D

    context['news'] = get_stock_news(id)
    context['form'] = form

    # Calculate price change and percentage change from open to current price
    open_price = close_prices[0]
    current_price = close_prices[-1]
    price_change = current_price - open_price
    percentage_change = (price_change / open_price) * 100

    # Create the plot using Plotly
    formatted_price_change = round(price_change, 2)
    formatted_percentage_change = round(percentage_change, 2)
    if price_change > 0:
        subtitle = f'Up ${formatted_price_change} ({formatted_percentage_change}%)'
    else:
        subtitle = f'Down ${formatted_price_change} ({formatted_percentage_change}%)'
    fig = go.Figure(data=go.Scatter(x=timestamps, y=close_prices))
    fig.update_layout(
        title={'text': f'${round(current_price, 2)}', 'y': 0.9, 'x': 0, 'xref': 'paper', 'yanchor': 'top'},
        annotations=[{'text': subtitle, 'showarrow': False, 'xref': 'paper', 'yref': 'paper', 'x': 0, 'y': 1.15, 'font': {'size': 14}}],
    )
    # Convert the plot to HTML and pass it to the template
    plot_data = pio.to_html(fig, full_html=False)
    context['plot_data'] = plot_data

    return render(request, 'stock.html', context)



