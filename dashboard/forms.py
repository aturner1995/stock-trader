from django import forms

class StockForm(forms.Form):
    stock = forms.CharField(label='Stock', max_length=5)
