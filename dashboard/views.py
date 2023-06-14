from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .forms import StockForm, NewUserForm, BuyStockForm
from .models import Profile, Stock, Transaction, WatchlistStock
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

    profile = Profile.objects.get(user=user)
    context['profile'] = profile
    total_value = profile.cash

    stocks = profile.user.stock_set.all()
    watchlist = profile.watchlist.all()

    for stock in stocks:
        current_price = get_current_stock_price(stock.symbol)
        stock.current_price = round(current_price["trades"][stock.symbol]["p"],2)
        stock.change = round((Decimal(stock.current_price) - (stock.average_purchase_price))/(stock.average_purchase_price)*100, 2)
        stock.value = round(stock.current_price * stock.quantity, 2)
        total_value += Decimal(stock.value)

    for stock in watchlist:
        current_price = get_current_stock_price(stock.symbol)
        stock.current_price = round(current_price["trades"][stock.symbol]["p"],2)
    
    context['stocks'] = stocks
    context['watch'] = watchlist
    context['form'] = StockForm()
    context['total_value'] = round(total_value, 2)

    return render(request, 'profile.html', context)

def stock(request, stock_symbol):
    context = {}
    context['stock'] = stock_symbol
    close_prices = []
    user = request.user
    existing_stock = Stock.objects.filter(user=user, symbol=stock_symbol).first()

    if request.method == 'POST':
        form = BuyStockForm(request.POST, initial={'stock_symbol': stock_symbol})
        close_prices, timestamps = get_stock_data(stock_symbol, '1D')
        if form.is_valid():
            # Process stock buying
            quantity = form.cleaned_data['quantity']
            price = Decimal(get_current_stock_price(stock_symbol)["trades"][stock_symbol]["p"])
            total_price = price * Decimal(quantity)
                            
            if user.profile.cash >= total_price:
                if existing_stock:
                    total_cost = existing_stock.average_purchase_price * existing_stock.quantity
                    total_cost += total_price
                    existing_stock.quantity += quantity
                    existing_stock.average_purchase_price = total_cost / existing_stock.quantity
                    existing_stock.save()
                else:
                    purchase = Stock(user=user, symbol=stock_symbol, quantity=quantity, average_purchase_price=price)
                    purchase.save()
                
                transaction = Transaction(stock=existing_stock or purchase, stock_symbol=stock_symbol, quantity=quantity, purchase_price=price, purchase=True)
                transaction.save()
                user.profile.cash -= total_price
                user.profile.save()
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
    context['existing_stock'] = existing_stock
    watchlist = Profile.objects.get(user=user).watchlist.all()
    watchlist_symbols = [item.symbol for item in watchlist]
    context['watchlist_symbols'] = watchlist_symbols
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


def sell_stock(request, stock_id):
    stock = Stock.objects.get(pk=stock_id)

    if request.method == 'POST':
        quantity = int(request.POST['quantity'])
        if quantity > 0 and quantity <= stock.quantity:
            price = Decimal(get_current_stock_price(stock.symbol)["trades"][stock.symbol]["p"])
            total_price = price * Decimal(quantity)

            # Update user balance
            user = request.user
            user.profile.cash += total_price
            user.profile.save()
            transaction = Transaction(stock=stock, stock_symbol=stock.symbol, quantity=quantity, purchase_price=price, purchase=False)
            transaction.save()

            # Update stock record
            stock.quantity -= quantity
            if stock.quantity == 0:
                stock.delete()
            else:
                stock.save()

            messages.success(request, f"You sold {quantity} shares of {stock.symbol} successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Invalid quantity or insufficient shares for selling.")

    return render(request, 'sell_stock.html', {'stock': stock})

     
def watchlist_toggle(request, stock_symbol):
    existing_stock = WatchlistStock.objects.filter(user=request.user, symbol=stock_symbol).first()
    
    if request.method == 'POST':       
        profile = Profile.objects.get(user=request.user)

        if existing_stock:
            profile.watchlist.remove(existing_stock)
            existing_stock.delete()
        else:
            watchlist_stock = WatchlistStock.objects.create(user=request.user, symbol=stock_symbol)
            profile.watchlist.add(watchlist_stock)
    
    return redirect('stock', stock_symbol=stock_symbol)