from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

TIME_PERIOD_CHOICES = [
    ('1D', '1 Day'),
    ('1W', '1 Week'),
    ('1M', '1 Month'),
    ('1Y', '1 Year'),
]

class StockForm(forms.Form):
    stock = forms.CharField(
        max_length=10,
        help_text='',
    )
    time_period = forms.ChoiceField(
        choices=TIME_PERIOD_CHOICES,
        initial='1D',
        widget=forms.HiddenInput(),
        help_text=''
    )

class BuyStockForm(forms.Form):
    quantity = forms.IntegerField(label='Quantity')
    stock_symbol = forms.CharField(widget=forms.HiddenInput())

class NewUserForm(UserCreationForm):

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    username = forms.CharField(
        max_length=150,
        help_text='',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    password2 = forms.CharField(
        label="Confirm Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
