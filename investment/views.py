from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from investment.forms import NewStrategyForm, AddPositionForm
from investment.models import Strategy, Transaction, Position
from decimal import Decimal

@login_required
def add_strategy(request):
    if request.method == 'POST':
        form = NewStrategyForm(request.POST, user=request.user, request=request)
        if form.is_valid():
            strategy, position = form.save()
            return redirect('strategies_list')
    else:
        form = NewStrategyForm(user=request.user)
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
def transactions_list(request, strategy_id):
    user = request.user
    strategy = get_object_or_404(Strategy, pk=strategy_id, user=user)
    transactions = Transaction.objects.filter(strategy=strategy).order_by('-date')

    context = {
        'strategy': strategy,
        'transactions': transactions,
    }
    return render(request, 'transactions_list.html', context)


@login_required
def positions(request, strategy_id):
    user = request.user
    strategy = get_object_or_404(Strategy, pk=strategy_id, user=user)
    positions = Position.objects.filter(strategy=strategy).order_by('symbol')

    market_value = []
    for position in positions:
        market_value.append(position.market_value())
    
    total_portfolio_value = sum(market_value)

    context = {
        'strategy': strategy, 
        'positions': positions,
        'total_portfolio_value': total_portfolio_value,
        }
    
    return render(request, 'positions.html', context)

@login_required
def add_position(request, strategy_id):
    user = request.user
    strategy = get_object_or_404(Strategy, pk=strategy_id, user=user)
    form = AddPositionForm()
    if request.method == 'POST':
        form = AddPositionForm(request.POST, user=user, strategy=strategy)
        if form.is_valid():
            user = request.user
            cleaned_data = form.clean_data()
            type = 'buy'
            symbol = cleaned_data['symbol'].upper()
            quantity = cleaned_data['quantity']
            cost = cleaned_data['cost']
            description = cleaned_data['description']
            date = cleaned_data['date']
            
            # Get the position for this symbol if exists
            try:
                position = Position.objects.get(user=request.user, symbol=symbol, strategy=strategy)
            except Position.DoesNotExist:
                position = None
            
            if position is None:
                position = Position.objects.create(
                user=user,
                strategy=strategy,
                symbol=symbol,   
                description=description,             
                quantity=quantity,
                cost = cost,
                )
                position.save()
                cash_position = Position.objects.get(user=user, symbol='*USD', strategy=strategy)
                cash_position.quantity -= cost * quantity
                cash_position.save()
            else:
                new_quantity = position.quantity + quantity
                new_cost = ((position.cost * position.quantity) + (cost * quantity)) / new_quantity
                position.quantity = new_quantity
                position.cost = new_cost
                position.save()
                cash_position = Position.objects.get(user=user, symbol='*USD', strategy=strategy)
                cash_position.quantity -= cost * quantity
                cash_position.save()

            # Create a new transaction
            transaction = Transaction.objects.create(
                user=user,
                strategy=strategy,
                type=type,
                symbol=symbol,
                quantity=quantity,
                price=cost,
                date=date,
                )
            transaction.save()
            return redirect('success')

    context = {
        'form': form
    }
    return render(request, 'add_position.html', context)

def success_view(request):
    return render(request, 'success.html')

def failure_view(request):
    return render(request, 'failure.html')