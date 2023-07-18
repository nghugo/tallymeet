from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.hashers import make_password
from django.urls import reverse, reverse_lazy
from passlib.handlers.django import django_pbkdf2_sha256
from django.contrib import messages

from .forms import PollPasswordForm, PollCreateForm, PollUpdatePasswordForm
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
    form_class = PollCreateForm
    template_name = 'poll/poll_create.html'  # override default poll_form.html'

    def get_form(self, form_class = PollCreateForm):  # just to override a label here
        form = super().get_form(form_class)
        form.fields['description'].label = "Description (optional)"
        return form
    
    def form_valid(self, form):  # Called when valid form data has been POSTed, returns HttpResponse
        # if use provided a poll password, add to session object, and hash it before saving to database
        if self.request.POST.get('poll_password'):
            self.request.session['pollPasswordAtPollCreation'] = self.request.POST.get('poll_password')  # pollPasswordAtPollCreation purpose -> do not have to re-entere when redirected to details
            poll_password_hashed = make_password(self.request.POST.get('poll_password'))  
            form.instance.poll_password = poll_password_hashed
        return super().form_valid(form)
    

def getEnteredPassword(requestSession, id):
    """ 
        Objective: return the latest correct poll password the user provided for a poll id
        -------------------------------------------------------------------
        Priorities:
        1. returns self.request.session['pollPasswordAtPollCreation'] if exists
            (most recent password is set after creating poll)
            (required because the object (hence its id) would not have been created by that point)
            (hence, we can't set requestSession['entered_password_dict'][id] yet)
        2. else returns requestSession['entered_password_dict'][id] if exists
            (represents the latest correct poll password the user provided for a poll id)
        3. else returns empty string ("") 
            (represents None, we redirect but do not flash the "wrong password" message)
    """
    entered_password_dict = requestSession.get('entered_password_dict', {})
    if 'pollPasswordAtPollCreation' in requestSession:
        entered_password_dict[id] = requestSession['pollPasswordAtPollCreation']  # mutate entered_password_dict to save the new password into the session object
        del requestSession['pollPasswordAtPollCreation']  # delete most recent password once used
    entered_password = entered_password_dict.get(id, "")
    return entered_password

class PollDetailView(DetailView):  # default template is poll/poll_detail.html
    model = Poll

    def get(self, request, *args, **kwargs):
        self.object= self.get_object()
        poll_password_hashed = self.object.poll_password
        id = str(self.object.__hash__())
        entered_password = getEnteredPassword(self.request.session, id)
        
        # if poll has a password and the user-provided-password does not exist or does not match -> redirect to password verification
        # in the "does not match" case, also show a flash message for user feedback
        if poll_password_hashed:
            if not entered_password:
                return redirect(reverse('poll-password') + "?id=" + str(id) + "&next=" + self.object.get_absolute_url())
            elif not django_pbkdf2_sha256.verify(entered_password, poll_password_hashed):
                messages.add_message(self.request, messages.ERROR, "Incorrect password")
                return redirect(reverse('poll-password') + "?id=" + str(id) + "&next=" + self.object.get_absolute_url())
            
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

class PollUpdateView(UpdateView):
    model = Poll
    fields = ['title', 'description', 'event_location']
    template_name = 'poll/poll_update.html'  # override default poll_form.html'

    def get(self, request, *args, **kwargs):
        self.object= self.get_object()
        poll_password_hashed = self.object.poll_password
        id = str(self.object.__hash__())
        entered_password = getEnteredPassword(self.request.session, id)

        # if poll has a password and the user-provided-password does not exist or does not match -> redirect to password verification
        # in the "does not match" case, also show a flash message for user feedback
        if poll_password_hashed:
            if not entered_password:
                return redirect(reverse('poll-password') + "?id=" + str(id) + "&next=" + self.object.get_absolute_url())
            elif not django_pbkdf2_sha256.verify(entered_password, poll_password_hashed):
                messages.add_message(self.request, messages.ERROR, "Incorrect password")
                return redirect(reverse('poll-password') + "?id=" + str(id) + "&next=" + self.object.get_absolute_url())
        
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subheading"] = "Info"
        return context

    def get_form(self, form_class = None):  # just to override 2 labels here
        form = super().get_form(form_class)
        form.fields['description'].label = "Description (optional)"
        form.fields['event_location'].label = "Event Location (optional)"
        return form

class PollUpdatePasswordView(UpdateView):
    model = Poll
    form_class = PollUpdatePasswordForm
    template_name = 'poll/poll_update.html'

    def get(self, request, *args, **kwargs):
        self.object= self.get_object()
        poll_password_hashed = self.object.poll_password
        id = str(self.object.__hash__())
        entered_password = getEnteredPassword(self.request.session, id)

        # if poll has a password and the user-provided-password does not exist or does not match -> redirect to password verification
        # in the "does not match" case, also show a flash message for user feedback
        if poll_password_hashed:
            if not entered_password:
                return redirect(reverse('poll-password') + "?id=" + str(id) + "&next=" + self.object.get_absolute_url())
            elif not django_pbkdf2_sha256.verify(entered_password, poll_password_hashed):
                messages.add_message(self.request, messages.ERROR, "Incorrect password")
                return redirect(reverse('poll-password') + "?id=" + str(id) + "&next=" + self.object.get_absolute_url())
                
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def form_valid(self, form):  # Called when valid form data has been POSTed, returns HttpResponse
        # if the user provided a new password for the poll, add to session object, and hash it before saving to database
        new_poll_password = self.request.POST.get('poll_password')
        
        if not new_poll_password:
            return super().form_valid(form)
        else:
            if super().form_valid(form):  # if form is valid, save the new password to the session object and db (hashed then handled by ModelForm)
                id = str(self.object.__hash__())
                self.request.session['entered_password_dict'][id] = new_poll_password
                # explicit save -> by default, Django does not save to session DB after mutation, only addition or deletion of values
            # see docs: https://docs.djangoproject.com/en/4.2/topics/http/sessions/#:~:text=When%20sessions%20are%20saved&text=To%20change%20this%20default%20behavior,has%20been%20created%20or%20modified.
                self.request.session.save()
                poll_password_hashed = make_password(new_poll_password)  
                form.instance.poll_password = poll_password_hashed
            return super().form_valid(form)

    def get_context_data(self, **kwargs):  # pass extra context to template
        context = super().get_context_data(**kwargs)
        context["subheading"] = "Password"
        return context

def poll_verify_password(request):
    if request.method == 'POST':
        form = PollPasswordForm(request.POST)
        if form.is_valid():
            next_url = request.GET.get('next')
            id = request.GET.get('id')
            if not next_url:
                return redirect('poll-home')
            # entered_password_dict maps id to the user-entered poll_password, ie entered_password
            if 'entered_password_dict' not in request.session:  
                request.session['entered_password_dict'] = {}
            request.session['entered_password_dict'][id] = form.cleaned_data['poll_password']
            # explicit save -> by default, Django does not save to session DB after mutation, only addition or deletion of values
            # see docs: https://docs.djangoproject.com/en/4.2/topics/http/sessions/#:~:text=When%20sessions%20are%20saved&text=To%20change%20this%20default%20behavior,has%20been%20created%20or%20modified.
            request.session.save()
            return redirect(next_url)
    else:  # GET request
        form = PollPasswordForm()
    return render(request, 'poll/poll_password.html', {'form': form})


class PollDeleteView(DeleteView):
    model = Poll
    success_url = reverse_lazy('poll-home')  # reverse cannot be used with success_url -> use reverse_lazy
    # success_url = "/"
    # default template is 'poll/poll_confirm_delete.html'

    def get(self, request, *args, **kwargs):
        self.object= self.get_object()
        poll_password_hashed = self.object.poll_password
        id = str(self.object.__hash__())
        entered_password = getEnteredPassword(self.request.session, id)

        # if poll has a password and the user-provided-password does not exist or does not match -> redirect to password verification
        # in the "does not match" case, also show a flash message for user feedback
        if poll_password_hashed:
            if not entered_password:
                return redirect(reverse('poll-password') + "?id=" + str(id) + "&next=" + self.object.get_absolute_url())
            elif not django_pbkdf2_sha256.verify(entered_password, poll_password_hashed):
                messages.add_message(self.request, messages.ERROR, "Incorrect password")
                return redirect(reverse('poll-password') + "?id=" + str(id) + "&next=" + self.object.get_absolute_url())
                
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

