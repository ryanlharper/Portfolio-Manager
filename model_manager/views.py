from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from model_manager.forms import SignUpForm

class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('home')
    template_name = 'register.html'
