from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from investment.forms import NewStrategyForm, AddPositionForm, SellPositionForm
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
def delete_strategy(request):
    if request.method == 'POST':
        strategy_id = request.POST.get('strategy')
        strategy = Strategy.objects.get(id=strategy_id, user=request.user)
        strategy.delete()
        return redirect('strategies_list')
    else:
        strategies = Strategy.objects.filter(user=request.user).order_by('name')
        context = {'strategies': strategies}
        return render(request, 'delete_strategy.html', context)

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
    total_day_return = []
    for position in positions:
        market_value.append(position.market_value())
        total_day_return.append(position.day_return()*(position.percent_portfolio()/100))
    
    total_portfolio_value = sum(market_value)
    total_day_pct_change = sum(total_day_return)

    context = {
        'strategy': strategy, 
        'positions': positions,
        'total_portfolio_value': total_portfolio_value,
        'total_day_pct_change': total_day_pct_change,
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
            
            cash_position = Position.objects.get(user=request.user, symbol='*USD', strategy=strategy)
            if cash_position.quantity < cost * quantity:
                return redirect('failure')                    
            
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
            return redirect('positions', strategy_id=strategy_id)

    context = {
        'form': form
    }
    return render(request, 'add_position.html', context)

def success_view(request):
    return render(request, 'success.html')

def failure_view(request):
    return render(request, 'failure.html')

def sell_position(request, strategy_id, symbol):
    strategy = get_object_or_404(Strategy, id=strategy_id)

    if request.method == 'POST':
        form = SellPositionForm(request.POST, symbol=symbol, strategy=strategy.id, user=request.user)
        if request.method == 'POST':
            if form.is_valid():
                # process the form data and redirect to a success page
                user = request.user
                cleaned_data = form.cleaned_data
                type = 'sell'
                symbol = symbol
                strategy = strategy
                quantity = cleaned_data['quantity']
                cost = cleaned_data['cost']
                date = cleaned_data['date']

                position = Position.objects.get(user=user, symbol=symbol, strategy=strategy)
                if quantity > position.quantity:
                    return redirect('failure')
                elif quantity < position.quantity:
                    new_quantity = position.quantity - quantity
                    position.quantity = new_quantity
                    position.save()
                    cash_position = Position.objects.get(user=user, symbol='*USD', strategy=strategy)
                    cash_position.quantity += cost * quantity
                    cash_position.save()
                else:
                    position_to_delete = Position.objects.get(user=user, symbol=symbol, strategy=strategy)
                    position_to_delete.delete()
                    cash_position = Position.objects.get(user=user, symbol='*USD', strategy=strategy)
                    cash_position.quantity += cost * quantity
                    cash_position.save()
                
                transaction = Transaction.objects.create(
                    user=user,
                    strategy=strategy,
                    type=type,
                    symbol=symbol,
                    quantity=quantity,
                    price=cost,
                    date=date
                )
                transaction.save()
                return redirect('positions', strategy_id=strategy.id)
                    
    else:
        form = SellPositionForm(symbol=symbol, strategy=strategy.id, user=request.user)

    context = {
        'form': form,
        'strategy': strategy,
        'symbol': symbol
    }

    return render(request, 'sell_position.html', context)
