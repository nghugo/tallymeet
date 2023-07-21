import datetime

from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.hashers import make_password
from django.urls import reverse, reverse_lazy
from passlib.handlers.django import django_pbkdf2_sha256
from django.contrib import messages

from .forms import PollOptionCreateForm, PollOptionCreateFormSet
from .models import PollOption
from poll.models import Poll

def pollOptionEdit(request):
    poll_id = str(request.GET.get('poll_id'))
    if request.method == 'POST':
        formset = PollOptionCreateFormSet(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.poll_id = Poll.objects.get(pk=request.GET.get('poll_id'))
                instance.save()
            messages.add_message(request, messages.INFO, "Form option update successful")
            return redirect('poll-detail', pk=poll_id)
        messages.add_message(request, messages.ERROR, "Form option update failed due to invalid form input (all updates aborted)")
    else:  # GET request
        formset = PollOptionCreateFormSet()
    
    return render(
        request, 
        template_name= "polloption/polloption_create.html", 
        context = {'formset': formset}
    )
