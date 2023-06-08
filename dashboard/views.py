from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .forms import StockForm, NewUserForm, BuyStockForm
from .models import Profile, Stock
from .fetchData import get_stock_data, get_stock_news, get_current_stock_price
import plotly.graph_objs as go
import plotly.io as pio
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from decimal import Decimal

def index(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.cleaned_data['stock']
            return HttpResponseRedirect(stock)
    else:
        form = StockForm()
    
    return render(request, 'index.html', {'form': form})

def register_request(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            balance = 100000
            profile = Profile(user=user, balance=balance)
            profile.save()
            login(request, user)
            messages.success(request, "Registration successful")
            return redirect('index')
        messages.error(request, 'Unsuccessful registration. Invalid information.')
    form = NewUserForm()
    return render(request, 'register.html', context={"register_form":form})

def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("index")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request, template_name="login.html", context={"login_form":form})

def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("index")

def profile(request):
    user = request.user
    context = {}

    context['profile'] = Profile.objects.get(user=user)
    context['form'] = StockForm()

    return render(request, 'profile.html', context)

def stock(request, stock_symbol):
    context = {}
    context['stock'] = stock_symbol
    close_prices = []

    if request.method == 'POST':
        form = BuyStockForm(request.POST, initial={'stock_symbol': stock_symbol})
        close_prices, timestamps = get_stock_data(stock_symbol, '1D')
        if form.is_valid():
            # Process stock buying
            user = request.user
            quantity = form.cleaned_data['quantity']
            price = Decimal(get_current_stock_price(stock_symbol)["trades"][stock_symbol]["p"])
            total_price = price * Decimal(quantity)
            print(user.profile.cash)
            if user.profile.cash >= total_price:
                user.profile.cash -= total_price
                user.profile.save()
                transaction = Stock(user=user, symbol=stock_symbol, quantity=quantity, purchase_price=price)
                transaction.save()
                messages.success(request, f"You bought {quantity} shares of {stock_symbol} successfully.")
            else:
                messages.error(request, "Insufficient balance to make the purchase.")
    else:
        form = StockForm()
        time_period = request.GET.get('time_period')
        if time_period:
            close_prices, timestamps = get_stock_data(stock_symbol, time_period)
        else:
            # Default time period is 1D
            close_prices, timestamps = get_stock_data(stock_symbol, '1D')

    context['news'] = get_stock_news(stock_symbol)
    context['form'] = form
    context['buystockform'] = BuyStockForm(initial={'stock_symbol': stock_symbol})
    # Calculate price change and percentage change from open to current price
    if close_prices:
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
