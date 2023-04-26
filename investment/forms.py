from django.contrib.auth.models import User
from django import forms
from investment.models import Strategy, Transaction
from django.forms.widgets import DateInput

class NewStrategyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(NewStrategyForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Strategy
        fields = ('name', 'type', 'asset_class', 'inception_date', 'mstar_id')
        widgets = {
            'inception_date': DateInput(),
        }
   
    name = forms.CharField(max_length=100)
    type = forms.ChoiceField(choices=Strategy.TYPE_CHOICES)
    asset_class = forms.ChoiceField(choices=Strategy.ASSET_CLASS_CHOICES)
    inception_date = forms.DateField(widget=DateInput(attrs={'type': 'date'}))
    mstar_id = forms.CharField(max_length=100, label='Morningstar ID', required=False)

    def clean_name(self):
        name = self.cleaned_data['name']
        user_id = self.request.user.id
        if Strategy.objects.filter(user_id=user_id, name=name).exists():
            raise forms.ValidationError("This strategy is already in use. Please use a different strategy name.")
        return name


class TransactionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['strategy'].choices = [(strategy.name, strategy.name) for strategy in Strategy.objects.filter(user=user)]
            
        
    class Meta:
        model = Transaction
        fields = ['strategy', 'type', 'symbol', 'allocation', 'price', 'date',]
        widgets = {
            'date': DateInput(attrs={'type': 'date'})
        }

    strategy = forms.ChoiceField(choices=[], required=True)
    type = forms.ChoiceField(choices=Transaction.TYPE_CHOICES, required=True)
    symbol = forms.CharField(max_length=8, required=True) # need to consider using the watchlist items here? (UPPER)?
    description = forms.CharField(max_length=128, required=True)
    allocation = forms.DecimalField(decimal_places=2, max_digits=10, required=True)
    price = forms.DecimalField(decimal_places=2, max_digits=10, required=True)
    date = forms.DateField(widget=DateInput(attrs={'type': 'date'}), required=True)