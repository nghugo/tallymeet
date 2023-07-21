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


class PollOptionCreateView(CreateView):  # CreateView
    model = PollOption
    
    form_class = PollOptionCreateForm  # original, but null data error
    # form_class = PollOptionCreateFormSet
    template_name = 'polloption/polloption_create.html'  # override default polloption/polloption_form.html'
    
    def get_form(self):
        if self.request.method == 'POST':
            return self.form_class(self.request.POST)
        return self.form_class()

    def get_success_url(self):
        return self.success_url 

    def get_initial(self):
        return {'poll_id': Poll.objects.get(pk=self.request.GET.get('poll_id'))}
    
    def form_valid(self, formset):  # Called when valid form data has been POSTed, returns HttpResponse
        """ Set poll_id as final field entry again, to prevent tampering """
        # form.instance.poll_id = self.request.GET.get('poll_id')  # temp disable DEBUG
        
        print("key, val received as:")
        for key, val in self.request.POST.items():
            print(key, val)

        instances = formset.save(commit=False)
        print(f"this is instances: {instances}")  # EMPTY LIST !!!!!
        for instance in instances:
            print(f"instance is {instance}")
            instance.poll_id = Poll.objects.get(pk=self.request.GET.get('poll_id'))
            instance.save()
        
        # return super().form_valid(formset)
        return redirect('poll-home')
        

    def post(self, request, *args, **kwargs):
        formset = PollOptionCreateFormSet(request.POST)
        print(f"**************** Formset is valid: {formset.is_valid()}")  # DEBUG
        print(f"The errors: {formset.errors}")
        print(f"The non-form errors: {formset.non_form_errors}")
        if formset.is_valid():
            return self.form_valid(formset)
        return render('poll-option-create')

        for key, val in self.request.POST.items():
            print(key, val)
        return redirect('poll-home')

    def get_context_data(self, **kwargs):  # pass formset as extra context to template
        context = super(PollOptionCreateView, self).get_context_data(**kwargs)
        initial=[{
            'poll_id': Poll.objects.get(pk=self.request.GET.get('poll_id')),
            # 'event_end_time': datetime.datetime.now()
            }]
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