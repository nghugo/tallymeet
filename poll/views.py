from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django import forms
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import PermissionRequiredMixin
from passlib.handlers.django import django_pbkdf2_sha256

from .forms import PollPasswordForm

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
        # if password exists, hash password before saving
        if self.request.POST.get('poll_password'):
            poll_password_hashed = make_password(self.request.POST.get('poll_password'))  
            form.instance.poll_password = poll_password_hashed
        return super().form_valid(form)

class PollDetailView(PermissionRequiredMixin, DetailView):  # default template is poll/poll_detail.html
    model = Poll

    login_url = '/poll/password/'
    permission_denied_message = 'Poll password required to access this page'

    def get(self, request, *args, **kwargs):
        self.object= self.get_object()
        poll_password_hashed = self.object.poll_password

        entered_password = self.request.session.get('entered_password', "")
        if poll_password_hashed and not django_pbkdf2_sha256.verify(entered_password, poll_password_hashed):
            return redirect('poll-password')
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    # def get_object(self):  # only get poll with no password or if password match
    #     obj = super().get_object()
    #     poll_password_hashed = obj.poll_password
    #     if not poll_password_hashed:  # poll has no password
    #         return obj
    #     else:  # poll has password
    #         entered_password = self.request.session.get('entered_password')
    #         if django_pbkdf2_sha256.verify(entered_password, poll_password_hashed):
    #             return obj
    #         else:
    #             redirect()

    # def dispatch(self, request, *args, **kwargs):
    #     if not self.request.user.has_profile():
    #         return redirect('users:userprofile')
    #     return super().dispatch(request, *args, **kwargs)

    # def get_context_data(self, *kwargs):
    #     context = super.get_context_date(**kwargs)

    def has_permission(self):  # this boolean can control 403 forbidden
        #  return self.request.user.email_confirmed
        return True


def poll_password(request):
    if request.method == 'POST':
        form = PollPasswordForm(request.POST)
        if form.is_valid():
            pass
            # check against context
            # return redirect # next parameter??
    else:  # GET request
        form = PollPasswordForm()

    return render(request, 'poll/poll_password.html', {'form': form})
    