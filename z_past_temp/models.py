from django.db import models
from django.contrib.auth.models import User
import yfinance as yf
from decimal import Decimal

class Strategy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)

    unique_together = (user,name)

    def __str__(self):
        return self.name

class Position(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=8)
    description = models.CharField(max_length=128, default="undetermined")
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=None)
    allocation = models.DecimalField(max_digits=10, decimal_places=2, default=None)
 
    def price(self):
        if self.symbol == '*USD':
            price = 1.00
            return price
        else:
            price = yf.Ticker(self.symbol).history(period='4d')['Close'].iloc[-1]
            return price

    
    def pct_change(self):
        if self.symbol == '*USD':
            pct_change = 0.00
            return pct_change
        else:  
            price = Decimal(str(yf.Ticker(self.symbol).history(period='4d')['Close'].iloc[-1]))
            cost = Decimal(str(self.cost))
            pct_change = ((price / cost) - Decimal('1')) * 100
            return float(pct_change)
    
    def day_return(self):
        if self.symbol == '*USD':
            day_return = 0
            return day_return
        else:
            begining_price = yf.Ticker(self.symbol).history(period='4d')['Close'].iloc[-2]
            realtime_price = yf.Ticker(self.symbol).history(period='4d')['Close'].iloc[-1]
            day_return = ((realtime_price / begining_price) - 1) * 100
            return day_return

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    TYPE_CHOICES = (
        ('buy', 'Buy to Open'),
        ('sell', 'Sell to Close'),
        ('update', 'Update Existing'),
    )
    type = models.CharField(choices=TYPE_CHOICES, max_length=6)
    symbol = models.CharField(max_length=8)
    allocation = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=None)
    date = models.DateField(default="2022-12-31")