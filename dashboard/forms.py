from django import forms

TIME_PERIOD_CHOICES = [
    ('1D', '1 Day'),
    ('1W', '1 Week'),
    ('1M', '1 Month'),
    ('1Y', '1 Year'),
]

class StockForm(forms.Form):
    stock = forms.CharField(max_length=10)
    time_period = forms.ChoiceField(choices=TIME_PERIOD_CHOICES, initial='1D', widget=forms.HiddenInput())
