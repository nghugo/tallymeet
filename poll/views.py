from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Poll
from django.contrib.auth.hashers import make_password
from django import forms

# Create your views here.

def home(request):
    return render(request, "poll/home.html", {'title': 'Tallymeet'})

def base(request):  # for debugging
    return render(request, "poll/base.html", {'title': 'BASE TEMPLATE'})

def happy(request):  # for debugging, no inheritance
    return render(request, "poll/happy.html")

# recall default template for class based view: APP/MODEL_VIEWTYPE.html

class PollCreateView(CreateView):  
    model = Poll
    fields = ['title', 'description', 'event_location', 'poll_password']
    template_name = 'poll/poll_create.html'  # override default poll_form.html'
    
    # change default labels and add help text on form
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['description'].label = 'Description (optional)'
        form.fields['event_location'].label = 'Event Location (optional)'
        form.fields['poll_password'].label = 'Poll Password (optional)'
        form.fields['poll_password'].widget = forms.PasswordInput()  # mask password on form
        form.fields['poll_password'].help_text = 'Set and share a poll password so only your group can access this poll'
        return form

    def form_valid(self, form):  # Called when valid form data has been POSTed, returns HttpResponse
        # hash password before saving
        poll_password_hashed = make_password(self.request.POST.get('poll_password'))  
        form.instance.poll_password = poll_password_hashed
        return super().form_valid(form)

class PollDetailView(DetailView):  # default template is poll/poll_detail.html
    model = Poll
    