from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from investment.models import Index

@receiver(post_migrate)
def populate_indexes(sender, **kwargs):
    if sender.name == 'investment':
        if not Index.objects.exists():
            Index.objects.create(symbol = '^GSPC', name='S&P 500')
            Index.objects.create(symbol = '^DJI', name='Dow Jones Industrial Average')
            Index.objects.create(symbol = '^IXIC', name='NASDAQ Composite')
            Index.objects.create(symbol = 'BTC-USD', name='Bitcoin USD')
            Index.objects.create(symbol = '^RUT', name='Russell 2000')
            Index.objects.create(symbol = '^VIX', name='CBOE Volatility Index')
            Index.objects.create(symbol = '^TNX', name='Treasury Yield 10 Years')
            
            