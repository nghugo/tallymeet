import uuid

from django.shortcuts import render, redirect
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.hashers import make_password
from django.urls import reverse, reverse_lazy
from passlib.handlers.django import django_pbkdf2_sha256
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseForbidden

from .forms import (PollPasswordForm, PollCreateForm, PollUpdatePasswordForm, 
                    PollVoteResponderMetaForm, PollVoteForm)
from .models import Poll
from .views_helper import getSavedPollPassword, getRankedResponses, addDenseRank
from .views_helper import get_item  # not explicitly called, but required for dictionary query inside template of DetailView 

from polloption.models import PollOption, PollOptionResponse
from user.models import User


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

        # Fetch counts for each poll option, sort, and add dense rank
        rankedResponses = getRankedResponses(self.object)      
        rankedResponses = addDenseRank(rankedResponses)

        # # DEBUG
        # for obj in rankedResponses:
        #     print(obj)
            
        context = self.get_context_data(
            object = self.object, 
            rankedResponses = rankedResponses,
            yKey = PollOptionResponse.YES, 
            pKey = PollOptionResponse.PREFER, 
            nKey = PollOptionResponse.NO, 
        )
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



# filter out existing pollOptionUserResponses in database
def getExisting_pollOptionUserResponses(request, pollOptions):
    """
        Given poll options and the user making the request (via the request object), 
        return the poll option responses that belong to the user making the request
        If this user is anonymous -> ID by uuid4
        If this user is authenticated -> ID by user.id
    """
    if not request.user.is_authenticated:
        pollOptionUserResponses = PollOptionResponse.objects.filter(
            poll_option_id__in = pollOptions, 
            responder_nonuser_id = request.session["nonUserId"]
        )
    else:
        pollOptionUserResponses = PollOptionResponse.objects.filter(
            poll_option_id__in = pollOptions, 
            responder_user_id = request.user.id
        )
    return pollOptionUserResponses


def vote(request, pk):
    pollOptions = PollOption.objects.filter(poll_id = pk)

    if not request.user.is_authenticated:
        if "nonUserId" not in request.session:
            request.session["nonUserId"] = str(uuid.uuid4())
    
    if request.method == 'POST':
        oAndVoteForms = []


        for index, o in enumerate(pollOptions):
            voteForm = PollVoteForm(request.POST, initial={'poll_option_id' : o}, prefix=str(index))
            oAndVoteForms.append((o, voteForm))
        metaForm = PollVoteResponderMetaForm(request.POST, initial={
            'responder_user_id': request.user.id if request.user.is_authenticated else None, 
            'responder_nonuser_id': request.session["nonUserId"] if not request.user.is_authenticated else None, 
        })

        # validate form and save to PollOptionResponses table (update entries if existing else create)
        allVoteFormsValid = True
        for _, voteForm in oAndVoteForms:
            allVoteFormsValid = allVoteFormsValid and voteForm.is_valid()
        

        if allVoteFormsValid and metaForm.is_valid():
            
            # if the same user has voted previously, delete them (since we want to update rather than create double the votes)
            pollOptionUserResponses = getExisting_pollOptionUserResponses(request, pollOptions)
            pollOptionUserResponses.delete()

            # save the new votes in database
            for _, voteForm in oAndVoteForms:
                vote = PollOptionResponse(    
                    poll_option_id = PollOption.objects.get(pk = voteForm["poll_option_id"].value()),
                    responder_user_id = User.objects.filter(pk=metaForm["responder_user_id"].value()).first(),  # get or None
                    responder_nonuser_id = metaForm["responder_nonuser_id"].value(),
                    responder_name = metaForm["main_responder_name"].value(),
                    response = voteForm["response"].value(),
                )
                vote.save()
            return redirect("poll-detail", pk=pk)

    else:  # GET request
        oAndVoteForms = []

        for index, o in enumerate(pollOptions):
            voteForm = PollVoteForm(initial={'poll_option_id' : o}, prefix=str(index))
            oAndVoteForms.append((o, voteForm))
        metaForm = PollVoteResponderMetaForm(initial={
            'responder_user_id': request.user.id if request.user.is_authenticated else None, 
            'responder_nonuser_id': request.session["nonUserId"] if not request.user.is_authenticated else None, 
        })
        if not request.user.is_authenticated:
            messages.add_message(request, messages.WARNING, "Warning: You are voting as a guest since you have not logged in. Hence, you cannot modify these votes if you use another web session.")

    return render(
        request, 'poll/poll_vote.html',
        {'oAndVoteForms': oAndVoteForms,
         'metaForm': metaForm, 
         'pk': pk
        }
    )
     