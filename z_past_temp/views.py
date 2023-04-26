from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from investment.forms import NewStrategyForm, AddPositionForm
from investment.models import Strategy, Transaction, Position

@login_required
def add_strategy(request):
    if request.method == 'POST':
        form = NewStrategyForm(request.POST, request=request)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            type = form.cleaned_data['type']
            asset_class = form.cleaned_data['asset_class']
            inception_date = form.cleaned_data['inception_date']
            mstar_id = form.cleaned_data['mstar_id']

            strategy = Strategy.objects.create(
                user=user,
                name=name,
                type=type,
                asset_class=asset_class,
                inception_date=inception_date,
                mstar_id=mstar_id,
            )
            strategy.save()
            return redirect('strategies_list')
    else:
        form = NewStrategyForm(request=request)
    return render(request, 'add_strategy.html', {'form': form})

@login_required
def strategies_list(request):
    strategies = Strategy.objects.filter(user=request.user).order_by('name')

    context = {
        'user': request.user,
        'strategies': strategies,
    }
    return render(request, 'strategies_list.html', context)

@login_required
def positions(request, strategy_id):
    user = request.user
    strategy = get_object_or_404(Strategy, pk=strategy_id, user=user)

    positions = Position.objects.filter(strategy=strategy).order_by('symbol')

    context = {'strategy': strategy, 'positions': positions}
    return render(request, 'positions.html', context)

@login_required
def add_position(request):          # NEED TO ADDRESS CSS
    user = request.user
    if request.method == 'POST':
        form = AddPositionForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            strategy = form.cleaned_data['strategy']
            type = 'buy'
            symbol = form.cleaned_data['symbol'].upper()
            description = form.cleaned_data['description']
            allocation = form.cleaned_data['allocation']
            price = form.cleaned_data['price']
            date = form.cleaned_data['date']
  
            if type == 'buy':
                #add to the transaction model
                transaction = Transaction.objects.create(
                        user = user,
                        strategy = strategy,
                        type = type,
                        symbol = symbol,
                        allocation = allocation,
                        price = price,
                        date = date,
                )
                transaction.save()

                #add to the position model
                position = Position.objects.create(
                    user = user,
                    strategy = strategy,
                    symbol = symbol ,
                    description = description,
                    cost = price,
                    allocation = allocation,
                )
                position.save()
                
                #update cash allocation
                cash_allocation = Position.objects.filter(user=user, symbol='*USD').first()
                if cash_allocation:
                    cash_allocation.allocation -= allocation
                    cash_allocation.save()
                    return redirect('positions', strategy_id=strategy.id)
                else:
                    return render(request, 'failure.html', context)

    else:
        form = AddPositionForm(user=user)
    context = {
        'form': form,
    }
    return render(request, 'add_position.html', context)

@login_required
def transactions_list(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('date')

    context = {
        'user': request.user,
        'transactions': transactions,
    }
    return render(request, 'transactions_list.html', context)