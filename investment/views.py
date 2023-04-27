from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from investment.forms import NewStrategyForm
from investment.models import Strategy, Transaction, Position

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
def transactions_list(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    # NEEDS TO consider only strategy

    context = {
        'user': request.user,
        'transactions': transactions,
    }
    return render(request, 'transactions_list.html', context)


@login_required
def positions(request, strategy_id):
    user = request.user
    strategy = get_object_or_404(Strategy, pk=strategy_id, user=user)
    positions = Position.objects.filter(strategy=strategy).order_by('symbol')

    context = {'strategy': strategy, 'positions': positions}
    return render(request, 'positions.html', context)