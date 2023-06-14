from django.db import models

from django.contrib.auth.models import User

class WatchlistStock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)
    added_date = models.DateField(auto_now_add=True)

class Stock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)
    average_purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    purchase_date = models.DateField(auto_now_add=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cash = models.DecimalField(max_digits=10, decimal_places=2, default=100000.00)
    watchlist = models.ManyToManyField(WatchlistStock)
    
class Transaction(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.SET_NULL, null=True)
    stock_symbol = models.CharField(max_length=10,default='')
    transaction_date = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase = models.BooleanField(default=False)
