from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.hashers import make_password
from django.urls import reverse, reverse_lazy
from passlib.handlers.django import django_pbkdf2_sha256
from django.contrib import messages

from .forms import PollOptionCreateForm, PollOptionCreateFormSet
from .models import PollOption
from poll.models import Poll


class PollOptionCreateView(CreateView):
    model = PollOption
    form_class = PollOptionCreateForm
    template_name = 'polloption/polloption_create.html'  # override default polloption/polloption_form.html'
    
    def get_initial(self):
        return {'poll_id':Poll.objects.get(pk=self.request.GET.get('poll_id'))}
    
    def form_valid(self, form):  # Called when valid form data has been POSTed, returns HttpResponse
        """ Set poll_id as final field entry again, to prevent tampering """
        form.instance.poll_id = self.request.GET.get('poll_id')
        return super().form_valid(form)
    
    # # # # # #
    # Formset #
    # # # # # #

    def get_context_data(self, **kwargs):  # pass extra context to template
        context = super().get_context_data(**kwargs)
        
        # multiplier controls the number of forms
        initial=[{'poll_id':Poll.objects.get(pk=self.request.GET.get('poll_id'))}] * 2
        context["formset"] = PollOptionCreateFormSet(initial=initial)
        return context

    # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #  use form_valid to validate against poll password #
    # # # # # # # # # # # # # # # # # # # # # # # # # # #

    #     def form_valid(self, form):  # Called when valid form data has been POSTed, returns HttpResponse
    #         # if use provided a poll password, add to session object, and hash it before saving to database
    #         if self.request.POST.get('poll_password'):
    #             self.request.session['pollPasswordAtPollCreation'] = self.request.POST.get('poll_password')  # pollPasswordAtPollCreation purpose -> do not have to re-enter when redirected to details
    #             poll_password_hashed = make_password(self.request.POST.get('poll_password'))  
    #             form.instance.poll_password = poll_password_hashed
    #         return super().form_valid(form)

class PollOptionDetailView(DetailView):
    model = PollOption
    # template is 'polloption/polloption_detail.html'