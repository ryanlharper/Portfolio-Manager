from pm.forms import SignUpForm
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('home')
    template_name = 'register.html'