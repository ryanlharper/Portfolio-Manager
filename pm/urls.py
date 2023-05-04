"""pm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from pm.views import SignUpView
from investment.views import add_strategy, strategies_list, transactions_list, positions
from investment.views import add_position, success_view, failure_view, delete_strategy
from investment.views import sell_position, increase_position, edit_strategy, add_watchlist
from investment.views import watchlist, watchlists_list, add_security, home, delete_watchlist
from investment.views import edit_watchlist, remove_security

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path('', home, name='home'),
    path('register/', SignUpView.as_view(), name='register'),
    path('add_strategy/', add_strategy, name='add_strategy'),
    path('add_watchlist/', add_watchlist, name='add_watchlist'),
    path('delete_strategy/', delete_strategy, name='delete_strategy'),
    path('strategies/', strategies_list, name='strategies_list'),
    path('transactions/<int:strategy_id>/', transactions_list, name='transactions_list'),
    path('positions/<int:strategy_id>/', positions, name='positions'),
    path('add_position/<int:strategy_id>/', add_position, name='add_position'),   
    path('success/', success_view, name='success'),   
    path('failure/', failure_view, name='failure'),   
    path('sell/<int:strategy_id>/<str:symbol>/', sell_position, name='sell_position'),
    path('increase/<int:strategy_id>/<str:symbol>/', increase_position, name='increase_position'),
    path('edit-strategy/', edit_strategy, name='edit_strategy'),
    path('watchlist/<int:watchlist_id>/', watchlist, name='watchlist'),
    path('watchlists/', watchlists_list, name='watchlists_list'),
    path('add_security/<int:watchlist_id>/', add_security, name='add_security'),
    path('delete_watchlist/', delete_watchlist, name='delete_watchlist'),
    path('edit_watchlist/', edit_watchlist, name='edit_watchlist'),
    path('remove_security/<int:watchlist_id>/<str:symbol>/', remove_security, name='remove_security'),

]
