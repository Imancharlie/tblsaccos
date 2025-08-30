from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

@login_required
def buy_shares(request):
    if request.method == 'POST':
        # Handle share purchase logic
        messages.success(request, 'Shares purchased successfully!')
        return redirect('shares:my_shares')
    
    context = {
        'share_price': 100,  # Example share price
        'available_shares': 1000,  # Example available shares
    }
    return render(request, 'shares/buy_shares.html', context)

@login_required
def my_shares(request):
    # Get user's shares
    context = {
        'total_shares': 50,  # Example: user has 50 shares
        'share_value': 5000,  # Example: 50 shares * $100
    }
    return render(request, 'shares/my_shares.html', context)

@login_required
def shares_history(request):
    # Get user's share transaction history
    context = {
        'transactions': [],  # Example: empty for now
    }
    return render(request, 'shares/shares_history.html', context)
