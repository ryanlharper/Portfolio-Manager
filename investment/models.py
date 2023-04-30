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

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    TYPE_CHOICES = (
        ('buy', 'Buy to Open'),
        ('sell', 'Sell to Close'),
    )
    type = models.CharField(choices=TYPE_CHOICES, max_length=6)
    symbol = models.CharField(max_length=8)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=None)
    date = models.DateField()

    def total(self):
        return self.price * self.quantity

class Position(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=8)
    quantity = models.DecimalField(max_digits=15, decimal_places=2, default=None)
    description = models.CharField(max_length=128, default="undetermined")
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=None)
        
    def __str__(self):
        return self.symbol
    
    def price(self):
        if self.symbol == '*USD':
            price = 1
            return price
        else:
            price = yf.Ticker(self.symbol).history(period='4d')['Close'].iloc[-1]
            return Decimal(price)
    
    def pct_change(self):
        if self.symbol == '*USD':
            pct_change = 0.00
            return pct_change
        else:  
            pct_change = ((self.price() / self.cost) - Decimal('1')) * 100
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
    
    def market_value(self):
        return float(self.quantity * self.price())
    
    def dollar_return(self):
        return((self.price() - self.cost)*self.quantity)

    def percent_portfolio(self):
        strategy_positions = Position.objects.filter(strategy=self.strategy)
        total_portfolio_value = sum(position.market_value() for position in strategy_positions)
        if total_portfolio_value == 0:
            percent_portfolio = 0
            return percent_portfolio
        else:
            return (self.market_value() / total_portfolio_value) * 100