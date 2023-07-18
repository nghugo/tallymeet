from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django import forms
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from passlib.handlers.django import django_pbkdf2_sha256

from .forms import PollPasswordForm, PollForm

from .models import Poll

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
    form_class = PollForm
    template_name = 'poll/poll_create.html'  # override default poll_form.html'

    def get_form(self, form_class = PollForm):
        form = super().get_form(form_class)
        form.fields['description'].label = "Description (optional)"
        return form
    
    def form_valid(self, form):  # Called when valid form data has been POSTed, returns HttpResponse
        # if password exists, hash password before saving
        if self.request.POST.get('poll_password'):
            poll_password_hashed = make_password(self.request.POST.get('poll_password'))  
            form.instance.poll_password = poll_password_hashed
        return super().form_valid(form)

class PollDetailView(DetailView):  # default template is poll/poll_detail.html
    model = Poll

    def get(self, request, *args, **kwargs):
        self.object= self.get_object()
        poll_password_hashed = self.object.poll_password
        entered_password_dict = self.request.session.get('entered_password_dict', {})  # default to empty dict
        entered_password = entered_password_dict.get(self.object.get_absolute_url(), "")  # default to empty str

        # redirect if poll has a password but user entered password does not match
        if poll_password_hashed and not django_pbkdf2_sha256.verify(entered_password, poll_password_hashed):
            return redirect(reverse('poll-password') + "?next=" + self.object.get_absolute_url())
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


def poll_password(request):
    if request.method == 'POST':
        form = PollPasswordForm(request.POST)
        if form.is_valid():
            
            next_url = request.GET.get('next')
            if not next_url:
                return redirect('poll-home')
            
            # entered_password_dict maps next_url to the user-entered poll_password, ie entered_password
            if 'entered_password_dict' not in request.session:  
                request.session['entered_password_dict'] = {}
            request.session['entered_password_dict'][next_url] = form.cleaned_data['poll_password']
            
            # explicitly tell Django to save to session database after modification
            # Django by default only saves to session database after dictionary values have been assigned or deleted
            # however, we are only mutating a value here
            # see docs: https://docs.djangoproject.com/en/4.2/topics/http/sessions/#:~:text=When%20sessions%20are%20saved&text=To%20change%20this%20default%20behavior,has%20been%20created%20or%20modified.
            request.session.save()
            
            return redirect(next_url)
            
            
    else:  # GET request
        form = PollPasswordForm()

    return render(request, 'poll/poll_password.html', {'form': form})
    