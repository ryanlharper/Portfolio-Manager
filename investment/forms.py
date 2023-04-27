from django.contrib.auth.models import User
from django import forms
from investment.models import Strategy, Transaction, Position

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