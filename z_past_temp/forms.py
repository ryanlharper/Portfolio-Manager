from django.contrib.auth.models import User
from django import forms
from investment.models import Strategy, Transaction, Position
from django.forms.widgets import DateInput

class NewStrategyForm(forms.Form):
    name = forms.CharField(max_length=100)
    value = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
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
            value=self.cleaned_data['value']
        )
        position = Position.objects.create(
            user=self.user,
            strategy=strategy,
            symbol='*USD',
            description='Cash',
            cost=1.00,
            quantity=strategy.value,
        )
        return strategy, position

class AddPositionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['strategy'].choices = [(strategy.id, strategy.name) for strategy in Strategy.objects.filter(user=user)]

             
    class Meta:
        model = Transaction
        fields = ['strategy', 'symbol', 'description', 'allocation', 'price', 'date',]
        widgets = {
            'date': DateInput(attrs={'type': 'date'})
        }

    strategy = forms.ChoiceField(choices=[], required=True)
    symbol = forms.CharField(max_length=8, required=True) # need to consider using the watchlist items here? (UPPER)?
    description = forms.CharField(max_length=128, required=True)
    allocation = forms.DecimalField(decimal_places=2, max_digits=10, required=True)
    price = forms.DecimalField(decimal_places=2, max_digits=10, required=True)
    date = forms.DateField(widget=DateInput(attrs={'type': 'date'}), required=True)

    def clean(self):
        cleaned_data = super().clean()
        strategy_id = cleaned_data.get('strategy')
        strategy = Strategy.objects.get(id=strategy_id)
        cleaned_data['strategy'] = strategy
        return cleaned_data