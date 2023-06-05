from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .forms import StockForm
from .tingo import get_meta_data

def index(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            stock = request.POST['stock']
            return HttpResponseRedirect(stock)
    else:
        form = StockForm()
        return render(request, 'index.html', {'form' : form})

def stock(request, id):
    context = {}
    context['stock'] = id
    context['meta'] = get_meta_data(id)
    return render(request, 'stock.html', context)

