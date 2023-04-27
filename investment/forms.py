from django.contrib.auth.models import User
from django import forms
from investment.models import Strategy, Transaction, Position
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
    widgets = {
            'date': DateInput(attrs={'type': 'date'})
        }
    
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
    
    def clean_data(self):
        cleaned_data = super().clean()
        symbol = cleaned_data.get('symbol').upper()
        quantity = cleaned_data.get('quantity')
        cost = cleaned_data.get('cost')
        description = cleaned_data.get('description')
        date = cleaned_data.get('date')

        # check if symbol is valid
        try:
            stock_info = yf.Ticker(symbol).history(period='1d')['Close'].iloc[-1]
        except:
            raise ValidationError("Invalid symbol")
        
        # check for positive quantity
        if quantity <=0:
            raise ValidationError("Quantity must be greater than zero.")
        
        # check for valid cost
        if cost <=0:
            raise ValidationError("Cost per share must be greater than zero.")

        cash_position = Position.objects.get(user=self.user, symbol='*USD', strategy=self.strategy)
        if cash_position.quantity < cost * quantity:
            raise forms.ValidationError("Insufficient funds.")

        return cleaned_data
