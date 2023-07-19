from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.hashers import make_password
from django.urls import reverse, reverse_lazy
from passlib.handlers.django import django_pbkdf2_sha256
from django.contrib import messages

from .forms import PollOptionCreateForm, PollOptionCreateFormSet
from .models import PollOption

# Create your views here.
class PollOptionCreateView(CreateView):
    model = PollOption
    form_class = PollOptionCreateForm
    template_name = 'polloption/polloption_create.html'  # override default polloption/polloption_form.html'
    
    def get_context_data(self, **kwargs):  # pass extra context to template
        context = super().get_context_data(**kwargs)
        context["PollOptionCreateFormSet"] = PollOptionCreateFormSet
        return context

# # # # # # # # # # # # # # # # # # # # # # # # # # #
#  use form_valid to validate against poll password #
# # # # # # # # # # # # # # # # # # # # # # # # # # #

#     def form_valid(self, form):  # Called when valid form data has been POSTed, returns HttpResponse
#         # if use provided a poll password, add to session object, and hash it before saving to database
#         if self.request.POST.get('poll_password'):
#             self.request.session['pollPasswordAtPollCreation'] = self.request.POST.get('poll_password')  # pollPasswordAtPollCreation purpose -> do not have to re-entere when redirected to details
#             poll_password_hashed = make_password(self.request.POST.get('poll_password'))  
#             form.instance.poll_password = poll_password_hashed
#         return super().form_valid(form)