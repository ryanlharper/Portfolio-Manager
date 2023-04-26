from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from model_manager.views import SignUpView
from investment.views import add_strategy, strategies_list, transactions_list, add_position
from investment.views import positions

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('register/', SignUpView.as_view(), name='register'),
    path('add_strategy/', add_strategy, name='add_strategy'),
    path('strategies/', strategies_list, name='strategies_list'),
    path('transactions/', transactions_list, name='transactions_list'),
    path('add_position/', add_position, name='add_position'),      
    path('positions/<int:strategy_id>/', positions, name='positions'),
]
