from django.shortcuts import render, redirect
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.hashers import make_password
from django.urls import reverse, reverse_lazy
from passlib.handlers.django import django_pbkdf2_sha256
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseForbidden

from .forms import PollPasswordForm, PollCreateForm, PollUpdatePasswordForm
from .models import Poll

from polloption.models import PollOption, PollOptionResponse

def home(request):
    return render(request, "poll/home.html", {'title': 'Tallymeet'})


def base(request):  # for debugging
    return render(request, "poll/base.html", {'title': 'BASE TEMPLATE'})


# default template for class based view: APP/MODEL_VIEWTYPE.html
class PollCreateView(SuccessMessageMixin, CreateView):  
    model = Poll
    form_class = PollCreateForm
    template_name = 'poll/poll_create.html'  # override default poll_form.html'
    success_message = "Poll created successfully"

    def get_form(self, form_class = PollCreateForm):  # just to override a label here
        form = super().get_form(form_class)
        form.fields['description'].label = "Description (optional)"
        return form
    
    def form_valid(self, form):  # Called when valid form data has been POSTed, returns HttpResponse
        # if use provided a poll password, add to session object, and hash it before saving to database
        if self.request.POST.get('poll_password'):
            self.request.session['pollPasswordAtPollCreation'] = self.request.POST.get('poll_password')  # pollPasswordAtPollCreation purpose -> do not have to re-enter when redirected to details
            poll_password_hashed = make_password(self.request.POST.get('poll_password'))  
            form.instance.poll_password = poll_password_hashed
        return super().form_valid(form)
    

def getSavedPollPassword(requestSession, id):
    """ Objective: return the latest correct poll password the user provided for a poll id, and also save it under poll_id key of the entered_password_dict in the session object
        -------------------------------------------------------------------
        Priorities:
        1. returns self.request.session['pollPasswordAtPollCreation'] if exists
            (most recent password is set after creating poll)
            (required because the object (hence its id) would not have been created by that point)
            (hence, we can't set requestSession['entered_password_dict'][id] yet)
        2. else returns requestSession['entered_password_dict'][id] if exists
            (represents the latest correct poll password the user provided for a poll id)
        3. else returns empty string ("") 
            (represents None, we redirect but do not flash the "wrong password" message) """
    
    if 'entered_password_dict' not in requestSession:
        requestSession['entered_password_dict'] = {}  # maps id (str) -> password (str)
    entered_password_dict = requestSession.get('entered_password_dict')

    if 'pollPasswordAtPollCreation' in requestSession:
        entered_password_dict[id] = requestSession['pollPasswordAtPollCreation']  # mutate entered_password_dict to save the new password into the session object
        del requestSession['pollPasswordAtPollCreation']  # delete most recent password once used
    
    # explicit save -> by default, Django does not save to session DB after mutation, only addition or deletion of values
    # see docs: https://docs.djangoproject.com/en/4.2/topics/http/sessions/#:~:text=When%20sessions%20are%20saved&text=To%20change%20this%20default%20behavior,has%20been%20created%20or%20modified.
    requestSession.save()
    
    entered_password = entered_password_dict.get(id, "")
    return entered_password

def getSorted_OptionsResponsesList(poll):
    """ Given a particular poll, returns an object voting results.
    The object contains all poll options and associated counts of PREFER, YES, and NO"""

    options = PollOption.objects.filter(poll_id = poll)
    optionsResponsesList = []   

    for option in options:
        responseToPeople = {PollOptionResponse.YES: [], PollOptionResponse.PREFER: [], PollOptionResponse.NO: []}
        for optionResponse in PollOptionResponse.objects.filter(poll_option_id = option):
            if optionResponse.response == PollOptionResponse.YES:
                responseToPeople[PollOptionResponse.YES].append(optionResponse.responder_name)
            elif optionResponse.response == PollOptionResponse.PREFER:
                responseToPeople[PollOptionResponse.PREFER].append(optionResponse.responder_name)
            else:
                responseToPeople[PollOptionResponse.NO].append(optionResponse.responder_name)
        optionsResponsesList.append([option, responseToPeople])

    # sort by YES count (desc) then PREFER count (desc)
    optionsResponsesList.sort(key = lambda obj: (-len(obj[1][PollOptionResponse.YES]), -len(obj[1][PollOptionResponse.PREFER])))
    for optionResponses in optionsResponsesList:
        print(optionResponses)

    return optionsResponsesList
    

class PollDetailView(DetailView):  # default template is poll/poll_detail.html
    model = Poll

    def get(self, request, *args, **kwargs):
        self.object= self.get_object()
        poll_password_hashed = self.object.poll_password
        id = str(self.object.__hash__())
        entered_password = getSavedPollPassword(self.request.session, id)
        
        # If poll has a password and the user-provided-password does not exist or does not match -> redirect to password verification
        # In the "does not match" case, also show a flash message for user feedback
        if poll_password_hashed:
            if not entered_password:
                return redirect(reverse('poll-verify-password') + "?id=" + str(id) + "&next=" + self.object.get_absolute_url())
            elif not django_pbkdf2_sha256.verify(entered_password, poll_password_hashed):
                messages.add_message(self.request, messages.ERROR, "Incorrect password")
                return redirect(reverse('poll-verify-password') + "?id=" + str(id) + "&next=" + self.object.get_absolute_url())

        # Fetch counts for each poll option
        sortedOptionResponsesList = getSorted_OptionsResponsesList(self.object)      
        
        # # DEBUG
        # print("Sorted **************")
        # for optionResponses in sortedOptionResponsesList:
        #     print(optionResponses)
        #     print()

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

class PollUpdateView(SuccessMessageMixin, UpdateView):
    model = Poll
    fields = ['title', 'description', 'event_location']
    template_name = 'poll/poll_update.html'  # override default poll_form.html'
    success_message = "Poll information updated successfully"

    def get(self, request, *args, **kwargs):
        self.object= self.get_object()
        poll_password_hashed = self.object.poll_password
        id = str(self.object.__hash__())
        entered_password = getSavedPollPassword(self.request.session, id)

        # if poll has a password and the user-provided-password does not exist or does not match -> redirect to password verification
        # in the "does not match" case, also show a flash message for user feedback
        if poll_password_hashed:
            if not entered_password:
                return redirect(reverse('poll-verify-password') + "?id=" + str(id) + "&next=" + self.object.get_absolute_url())
            elif not django_pbkdf2_sha256.verify(entered_password, poll_password_hashed):
                messages.add_message(self.request, messages.ERROR, "Incorrect password")
                return redirect(reverse('poll-verify-password') + "?id=" + str(id) + "&next=" + self.object.get_absolute_url())
        
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):  # pass extra context to template
        context = super().get_context_data(**kwargs)
        context["subheading"] = "Information"
        return context

    def get_form(self, form_class = None):  # just to override 2 labels here
        form = super().get_form(form_class)
        form.fields['description'].label = "Description (optional)"
        form.fields['event_location'].label = "Event Location (optional)"
        return form

    def post(self, request, *args, **kwargs):
        """ Add code before post() for poll password authentication """
        self.object= self.get_object()
        poll_password_hashed = self.object.poll_password
        id = str(self.object.__hash__())
        entered_password = getSavedPollPassword(self.request.session, id)

        if poll_password_hashed and (not entered_password or not django_pbkdf2_sha256.verify(entered_password, poll_password_hashed)):
            return HttpResponseForbidden()
        return super().post(request, *args, **kwargs)

class PollUpdatePasswordView(UpdateView):
    model = Poll
    form_class = PollUpdatePasswordForm
    template_name = 'poll/poll_update.html'

    def get(self, request, *args, **kwargs):
        self.object= self.get_object()
        poll_password_hashed = self.object.poll_password
        id = str(self.object.__hash__())
        entered_password = getSavedPollPassword(self.request.session, id)

        # if poll has a password and the user-provided-password does not exist or does not match -> redirect to password verification
        # in the "does not match" case, also show a flash message for user feedback
        if poll_password_hashed:
            if not entered_password:
                return redirect(reverse('poll-verify-password') + "?id=" + str(id) + "&next=" + self.object.get_absolute_url())
            elif not django_pbkdf2_sha256.verify(entered_password, poll_password_hashed):
                messages.add_message(self.request, messages.ERROR, "Incorrect password")
                return redirect(reverse('poll-verify-password') + "?id=" + str(id) + "&next=" + self.object.get_absolute_url())

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def form_valid(self, form):  # Called when valid form data has been POSTed, returns HttpResponse
        # if the user provided a new password for the poll, add to session object, and hash it before saving to database
        new_poll_password = self.request.POST.get('poll_password')
        
        if new_poll_password:
            if super().form_valid(form):  # if form is valid, save the new password to the session object and db (hashed then handled by ModelForm)
                id = str(self.object.__hash__())
                self.request.session['entered_password_dict'][id] = new_poll_password
                # explicit save -> by default, Django does not save to session DB after mutation, only addition or deletion of values
                # see docs: https://docs.djangoproject.com/en/4.2/topics/http/sessions/#:~:text=When%20sessions%20are%20saved&text=To%20change%20this%20default%20behavior,has%20been%20created%20or%20modified.
                self.request.session.save()
                poll_password_hashed = make_password(new_poll_password)  
                form.instance.poll_password = poll_password_hashed
        messages.add_message(self.request, messages.SUCCESS, "Poll password updated successfully")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):  # pass extra context to template
        context = super().get_context_data(**kwargs)
        context["subheading"] = "Password"
        return context
    
    def post(self, request, *args, **kwargs):
        """ Add code before post() for poll password authentication """
        self.object= self.get_object()
        poll_password_hashed = self.object.poll_password
        id = str(self.object.__hash__())
        entered_password = getSavedPollPassword(self.request.session, id)
        
        if poll_password_hashed and (not entered_password or not django_pbkdf2_sha256.verify(entered_password, poll_password_hashed)):
            return HttpResponseForbidden()
        return super().post(request, *args, **kwargs)

def poll_verify_password(request):
    if request.method == 'POST':
        form = PollPasswordForm(request.POST)
        if form.is_valid():
            next_url = request.GET.get('next')
            id = request.GET.get('id')
            if not next_url:
                messages.add_message(request, messages.ERROR, "No next URL to redirect to")
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

def poll_verify_password_redirect_with_poll_id(request):
    if request.method == 'POST':
        form = PollPasswordForm(request.POST)
        if form.is_valid():
            next_url = request.GET.get('next')
            id = request.GET.get('id')
            poll_id = request.GET.get('poll_id')  # FETCH POLL ID FROM URL
            if not next_url:
                messages.add_message(request, messages.ERROR, "No next URL to redirect to")
                return redirect('poll-home')
            # entered_password_dict maps id to the user-entered poll_password, ie entered_password
            if 'entered_password_dict' not in request.session:  
                request.session['entered_password_dict'] = {}
            request.session['entered_password_dict'][id] = form.cleaned_data['poll_password']
            # explicit save -> by default, Django does not save to session DB after mutation, only addition or deletion of values
            # see docs: https://docs.djangoproject.com/en/4.2/topics/http/sessions/#:~:text=When%20sessions%20are%20saved&text=To%20change%20this%20default%20behavior,has%20been%20created%20or%20modified.
            request.session.save()
            return redirect(next_url + "?poll_id=" + str(poll_id))  # REDIRECT WTIH POLL ID
    else:  # GET request
        form = PollPasswordForm()
    return render(request, 'poll/poll_password.html', {'form': form})


class PollDeleteView(SuccessMessageMixin, DeleteView):
    model = Poll
    # default template is 'poll/poll_confirm_delete.html'
    success_url = reverse_lazy('poll-home')  # reverse cannot be used with success_url -> use reverse_lazy
    success_message = "Poll deleted successfully"

    def get(self, request, *args, **kwargs):
        self.object= self.get_object()
        poll_password_hashed = self.object.poll_password
        id = str(self.object.__hash__())
        entered_password = getSavedPollPassword(self.request.session, id)

        # if poll has a password and the user-provided-password does not exist or does not match -> redirect to password verification
        # in the "does not match" case, also show a flash message for user feedback
        if poll_password_hashed:
            if not entered_password:
                return redirect(reverse('poll-verify-password') + "?id=" + str(id) + "&next=" + self.object.get_absolute_url())
            elif not django_pbkdf2_sha256.verify(entered_password, poll_password_hashed):
                messages.add_message(self.request, messages.ERROR, "Incorrect password")
                return redirect(reverse('poll-verify-password') + "?id=" + str(id) + "&next=" + self.object.get_absolute_url())
                
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """ Add code before post() for poll password authentication """
        self.object= self.get_object()
        poll_password_hashed = self.object.poll_password
        id = str(self.object.__hash__())
        entered_password = getSavedPollPassword(self.request.session, id)
        
        if poll_password_hashed and (not entered_password or not django_pbkdf2_sha256.verify(entered_password, poll_password_hashed)):
            return HttpResponseForbidden()
        return super().post(request, *args, **kwargs)
