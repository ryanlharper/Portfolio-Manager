from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from investment.forms import NewStrategyForm, AddPositionForm, NewWatchlistForm, RemoveWatchlistItemForm
from investment.forms import EditWatchlistForm, AddSecurityForm, SellPositionForm, IncreasePositionForm, EditStrategyForm
from investment.models import Strategy, Transaction, Position, Watchlist, WatchedStock, Index
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
def edit_strategy(request):
    strategies = Strategy.objects.filter(user=request.user).order_by('name')
    form = EditStrategyForm(request.POST or None)

    if request.method == 'POST':
        strategy_id = request.POST.get('strategy')
        strategy = Strategy.objects.get(id=strategy_id, user=request.user)
        form = EditStrategyForm(request.POST, instance=strategy)
        if form.is_valid():
            form.save()
            return redirect('strategies_list')

    context = {'strategies': strategies, 'form': form}
    return render(request, 'edit_strategy.html', context)

@login_required
def strategies_list(request):
    strategies = Strategy.objects.filter(user=request.user).order_by('name')
    watchlists = Watchlist.objects.filter(user=request.user).order_by('name')

    context = {
        'user': request.user,
        'strategies': strategies,
        'watchlists': watchlists
    }
    return render(request, 'strategies_list.html', context)

@login_required
def transactions_list(request, strategy_id):
    user = request.user
    strategy = get_object_or_404(Strategy, pk=strategy_id, user=user)
    transactions = Transaction.objects.filter(strategy=strategy).order_by('-date')
    strategies = Strategy.objects.filter(user=request.user).order_by('name')
    watchlists = Watchlist.objects.filter(user=request.user).order_by('name')

    context = {
        'strategy': strategy,
        'transactions': transactions,
        'strategies': strategies,
        'watchlists': watchlists,
    }
    return render(request, 'transactions_list.html', context)


@login_required
def positions(request, strategy_id):
    user = request.user
    strategy = get_object_or_404(Strategy, pk=strategy_id, user=user)
    positions = Position.objects.filter(strategy=strategy).order_by('symbol')
    strategies = Strategy.objects.filter(user=request.user).order_by('name')
    watchlists = Watchlist.objects.filter(user=request.user).order_by('name')

    market_value = []
    total_day_return = []
    total_dollar_return = []
    for position in positions:
        if position.symbol =='*USD':
            market_value.append(position.market_value())
            total_day_return.append(0.0)
            total_dollar_return.append(0.0)
        else:
            market_value.append(position.market_value())
            total_day_return.append(position.day_return()*(position.percent_portfolio()/100))
            total_dollar_return.append(position.dollar_return())
    
    total_portfolio_value = sum(market_value)
    total_day_pct_change = sum(total_day_return)
    total_dollar_return = sum(total_dollar_return)

    context = {
        'strategy': strategy, 
        'positions': positions,
        'total_portfolio_value': total_portfolio_value,
        'total_day_pct_change': total_day_pct_change,
        'strategies': strategies,
        'watchlists': watchlists,
        'total_dollar_return': total_dollar_return,
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
            
            if symbol == '*USD' and cost != 1.00:
                return redirect('failure')
            
            # Get the position for this symbol if exists
            try:
                position = Position.objects.get(user=request.user, symbol=symbol, strategy=strategy)
            except Position.DoesNotExist:
                position = None
            
            cash_position = Position.objects.get(user=request.user, symbol='*USD', strategy=strategy)
            
            if symbol != "*USD":
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
                if symbol == '*USD':
                    cash_position.quantity += quantity
                    cash_position.save() 
                else:
                    new_quantity = position.quantity + quantity
                    new_cost = ((position.cost * position.quantity) + (cost * quantity)) / new_quantity
                    position.quantity = new_quantity
                    position.cost = new_cost
                    position.save()
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
        'form': form,
        'strategy': strategy,
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

            if symbol == '*USD' and cost != 1.00:
                return redirect('failure')

            position = Position.objects.get(user=user, symbol=symbol, strategy=strategy)
            cash_position = Position.objects.get(user=user, symbol='*USD', strategy=strategy)
            if quantity > position.quantity:
                return redirect('failure')
            elif quantity < position.quantity:
                if symbol == '*USD':
                    cash_position.quantity -= quantity
                    cash_position.save()
                else:
                    new_quantity = position.quantity - quantity
                    position.quantity = new_quantity
                    position.save()
                    cash_position.quantity += cost * quantity
                    cash_position.save()
            else:
                if symbol == '*USD':
                    cash_position.quantity -= quantity
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
            return redirect('success')
                
    else:
        form = SellPositionForm(symbol=symbol, strategy=strategy.id, user=request.user)

    context = {
        'form': form,
        'strategy': strategy,
        'symbol': symbol
    }

    return render(request, 'sell_position.html', context)

@login_required
def increase_position(request, strategy_id, symbol):
    strategy = get_object_or_404(Strategy, id=strategy_id)

    if request.method == 'POST':
        form = IncreasePositionForm(request.POST, symbol=symbol, strategy=strategy.id, user=request.user)
        if form.is_valid():
            # process the form data and redirect to a success page
            user = request.user
            cleaned_data = form.cleaned_data
            type = 'buy'
            symbol = symbol
            strategy = strategy
            quantity = cleaned_data['quantity']
            cost = cleaned_data['cost']
            date = cleaned_data['date']

            position = Position.objects.get(user=user, symbol=symbol, strategy=strategy)
            cash_position = Position.objects.get(user=request.user, symbol='*USD', strategy=strategy)

            if symbol == "*USD":
                if cost != 1.00:
                    return redirect('failure') 
                else:
                    cash_position.quantity += quantity
                    cash_position.save()
            else:
                if cash_position.quantity < cost * quantity:
                    return redirect('failure') 
                else:
                    new_quantity = position.quantity + quantity
                    new_cost = ((position.cost * position.quantity) + (cost * quantity)) / new_quantity
                    position.quantity = new_quantity
                    position.cost = new_cost
                    position.save()
                    cash_position = Position.objects.get(user=user, symbol='*USD', strategy=strategy)
                    cash_position.quantity -= cost * quantity
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
            return redirect('success')
    
    else:
        form = IncreasePositionForm(symbol=symbol, strategy=strategy.id, user=request.user)

    context = {
        'form': form,
        'strategy': strategy,
        'symbol': symbol
    }

    return render(request, 'increase_position.html', context)

@login_required
def add_watchlist(request):
    if request.method == 'POST':
        form = NewWatchlistForm(request.POST, user=request.user, request=request)
        if form.is_valid():
            watchlist = form.save()
            return redirect('watchlists_list')
    else:
        form = NewWatchlistForm(user=request.user)
    return render(request, 'add_watchlist.html', {'form': form})

@login_required
def watchlist(request, watchlist_id):
    user = request.user
    watchlist = get_object_or_404(Watchlist, pk=watchlist_id, user=user)
    symbols = WatchedStock.objects.filter(watchlist=watchlist).order_by('symbol')
    strategies = Strategy.objects.filter(user=request.user).order_by('name')
    watchlists = Watchlist.objects.filter(user=request.user).order_by('name')

    context = {
        'watchlist': watchlist, 
        'symbols': symbols,
        'strategies': strategies,
        'watchlists': watchlists,
        }
    return render(request, 'watchlist.html', context)

@login_required
def watchlists_list(request):
    watchlists = Watchlist.objects.filter(user=request.user).order_by('name')
    strategies = Strategy.objects.filter(user=request.user).order_by('name')

    context = {
        'user': request.user,
        'watchlists': watchlists,
        'strategies': strategies
    }
    return render(request, 'watchlists_list.html', context)

@login_required
def add_security(request, watchlist_id):
    user = request.user
    watchlist = get_object_or_404(Watchlist, pk=watchlist_id, user=user)
    if request.method == 'POST':
        form = AddSecurityForm(request.POST, user=user, watchlist=watchlist)
        if form.is_valid():
            user = request.user
            cleaned_data = form.clean_data()
            symbol = cleaned_data['symbol'].upper()
            
            # Get the wacthlist item for this symbol if exists
            watchlist_item = WatchedStock.objects.filter(user=user, symbol=symbol, watchlist=watchlist).first()
            if watchlist_item:
                return redirect('failure') 
            else:
                watchlist_item = WatchedStock.objects.create(
                user=user,
                watchlist = watchlist,
                symbol=symbol,   
                )
                watchlist_item.save()
            return redirect('success')
    else:
        form = AddSecurityForm(user=request.user)

    context = {
        'form': form,
        'watchlist': watchlist,
    }
    return render(request, 'add_security.html', context)

from .models import Strategy, Watchlist

@login_required
def home(request):
    user = request.user
    strategies = Strategy.objects.filter(user=user)
    watchlists = Watchlist.objects.filter(user=user)
    indexes = Index.objects.all()
    context = {
        'strategies': strategies,
        'watchlists': watchlists,
        'indexes':indexes
    }
    return render(request, 'home.html', context)

@login_required
def delete_watchlist(request):
    if request.method == 'POST':
        watchlist_id = request.POST.get('watchlist')
        watchlist = Watchlist.objects.get(id=watchlist_id, user=request.user)
        watchlist.delete()
        return redirect('watchlists_list')
    else:
        watchlists = Watchlist.objects.filter(user=request.user).order_by('name')
        context = {'watchlists': watchlists}
        return render(request, 'delete_watchlist.html', context)


@login_required
def edit_watchlist(request):
    watchlists = Watchlist.objects.filter(user=request.user).order_by('name')
    form = EditWatchlistForm(request.POST or None)

    if request.method == 'POST':
        watchlist_id = request.POST.get('watchlist')
        watchlist = Watchlist.objects.get(id=watchlist_id, user=request.user)
        form = EditWatchlistForm(request.POST, instance=watchlist)
        if form.is_valid():
            form.save()
            return redirect('watchlists_list')

    context = {'watchlists': watchlists, 'form': form}
    return render(request, 'edit_watchlist.html', context)

@login_required
def remove_security(request, watchlist_id, symbol):
    watchlist = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)

    if request.method == 'POST':
        form = RemoveWatchlistItemForm(request.POST, user=request.user, symbol=symbol, watchlist_id=watchlist_id)
        if form.is_valid():
            watchlist_item = WatchedStock.objects.get(watchlist=form.cleaned_data['watchlist'], symbol=symbol)
            watchlist_item.delete()
            return redirect('success')
    else:
        form = RemoveWatchlistItemForm(user=request.user, watchlist_id=watchlist_id, symbol=symbol)

    context = {
        'form': form,
        'watchlist': watchlist,
        'symbol': symbol
    }

    return render(request, 'remove_security.html', context)