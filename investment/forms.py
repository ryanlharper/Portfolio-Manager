from django.contrib.auth.models import User
from django import forms
from investment.models import Strategy, Transaction, Position, Watchlist
from django.forms.widgets import DateInput
from django.core.exceptions import ValidationError
import yfinance as yf

class NewStrategyForm(forms.Form):
    name = forms.CharField(max_length=100)
    value = forms.DecimalField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.request = kwargs.pop('request', None)
        super(NewStrategyForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data['name']
        if Strategy.objects.filter(user=self.user, name=name).exists():
            raise forms.ValidationError("This strategy is already in use. Please use a different strategy name.")
        return name
    
    def clean_value(self):
        value = self.cleaned_data['value']
        if value <=0:
            raise forms.ValidationError("Value must be greater than zero.")
        return value

    def save(self):
        strategy = Strategy.objects.create(
            user=self.user,
            name=self.cleaned_data['name'],
        )
        position = Position.objects.create(
            user=self.user,
            strategy=strategy,
            symbol='*USD',
            description='Cash',
            cost=1.00,
            quantity=self.cleaned_data['value']
        )
        return strategy, position
    
class AddPositionForm(forms.Form):   
    symbol = forms.CharField(max_length=8, required=True)
    description = forms.CharField(max_length=128, required=True) 
    quantity = forms.DecimalField(decimal_places=2, max_digits=10, required=True)
    cost = forms.DecimalField(decimal_places=2, max_digits=10, required=True, label='Cost per Share')
    date = forms.DateField(widget=DateInput(attrs={'type': 'date'}), required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.strategy = kwargs.pop('strategy', None)
        self.request = kwargs.pop('request', None)
        super(AddPositionForm, self).__init__(*args, **kwargs)   
    
    def clean_symbol(self):
        symbol = self.cleaned_data['symbol']
        try:
            stock_info = yf.Ticker(symbol).history(period='1d')['Close'].iloc[-1]
        except:
            raise ValidationError("Invalid symbol")
        return symbol
    
    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity <=0:
            raise ValidationError("Quantity must be greater than zero.")
        return quantity
    
    def clean_cost(self):
        cost = self.cleaned_data['cost']
        if cost <=0:
            raise ValidationError("Cost must be greater than zero.")
        return cost
        
    def clean_data(self):
        cleaned_data = super().clean()
        symbol = cleaned_data.get('symbol').upper()
        quantity = cleaned_data.get('quantity')
        cost = cleaned_data.get('cost')
        description = cleaned_data.get('description')
        date = cleaned_data.get('date')

        return cleaned_data
    
class SellPositionForm(forms.Form):
    symbol = forms.CharField(widget=forms.HiddenInput())
    strategy = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.DecimalField(decimal_places=2, max_digits=20)
    cost = forms.DecimalField(decimal_places=2, max_digits=20, label='Price per Share')
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        symbol = kwargs.pop('symbol')
        strategy = kwargs.pop('strategy')
        super().__init__(*args, **kwargs)
        self.fields['symbol'].initial = symbol
        self.fields['strategy'].initial = strategy
        self.fields['quantity'].initial = Position.objects.get(user=user, symbol=symbol, strategy=strategy).quantity
        self.user = user

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity <=0:
            raise ValidationError("Quantity must be greater than zero.")
        return quantity

    def clean_cost(self):
        cost = self.cleaned_data['cost']
        if cost <=0:
            raise ValidationError("Cost must be greater than zero.")
        return cost

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        cost = cleaned_data.get('cost')
        date = cleaned_data.get('date')
        return cleaned_data
    
class IncreasePositionForm(forms.Form):
    symbol = forms.CharField(widget=forms.HiddenInput())
    strategy = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.DecimalField(decimal_places=2, max_digits=20)
    cost = forms.DecimalField(decimal_places=2, max_digits=20, label='Price per Share')
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        symbol = kwargs.pop('symbol')
        strategy = kwargs.pop('strategy')
        super().__init__(*args, **kwargs)
        self.fields['symbol'].initial = symbol
        self.fields['strategy'].initial = strategy
        self.user = user

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity <=0:
            raise ValidationError("Quantity must be greater than zero.")
        return quantity

    def clean_cost(self):
        cost = self.cleaned_data['cost']
        if cost <=0:
            raise ValidationError("Cost must be greater than zero.")
        return cost

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        cost = cleaned_data.get('cost')
        date = cleaned_data.get('date')
        return cleaned_data

class EditStrategyForm(forms.ModelForm):
    class Meta:
        model = Strategy
        fields = ['name']

class NewWatchlistForm(forms.Form):
    name = forms.CharField(max_length=100)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.request = kwargs.pop('request', None)
        super(NewWatchlistForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data['name']
        if Watchlist.objects.filter(user=self.user, name=name).exists():
            raise forms.ValidationError("This watchlist is already in use. Please use a different strategy name.")
        return name

    def save(self):
        watchlist = Watchlist.objects.create(
            user=self.user,
            name=self.cleaned_data['name'],
        )
        return watchlist
    
class AddSecurityForm(forms.Form):   
    symbol = forms.CharField(max_length=8, required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.watchlist = kwargs.pop('watchlist', None)
        self.request = kwargs.pop('request', None)
        super(AddSecurityForm, self).__init__(*args, **kwargs)   
    
    def clean_symbol(self):
        symbol = self.cleaned_data['symbol']
        try:
            stock_info = yf.Ticker(symbol).history(period='1d')['Close'].iloc[-1]
        except:
            raise ValidationError("Invalid symbol")
        return symbol

    def clean_data(self):
        cleaned_data = super().clean()
        symbol = cleaned_data.get('symbol').upper()
        if not symbol:
            raise ValidationError("Symbol is required.")
        return cleaned_data
    
class EditWatchlistForm(forms.ModelForm):
    class Meta:
        model = Watchlist
        fields = ['name']