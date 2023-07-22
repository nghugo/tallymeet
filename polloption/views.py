import datetime

from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.hashers import make_password
from django.urls import reverse, reverse_lazy
from passlib.handlers.django import django_pbkdf2_sha256
from django.contrib import messages

from .forms import PollOptionEditFormSet, PollOptionEditForm
from .models import PollOption
from poll.models import Poll

def pollOptionEdit(request):
    poll_id = str(request.GET.get('poll_id'))

    if request.method == 'POST':
        formset = PollOptionEditFormSet(request.POST, queryset = PollOption.objects.filter(poll_id=poll_id))
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.poll_id = Poll.objects.get(pk=request.GET.get('poll_id'))
                instance.save()
            messages.add_message(request, messages.INFO, "Poll option updated successfully")
            return redirect('poll-detail', pk=poll_id)
        messages.add_message(request, messages.ERROR, "Poll option update failed due to invalid form input (all updates aborted)")
    
    else:  # GET request
        formset = PollOptionEditFormSet(queryset = PollOption.objects.filter(poll_id=poll_id))
    
    return render(  # render request in template, and add context to template
        request, 
        template_name= "polloption/polloption_edit.html", 
        context = {'formset': formset, 'pollid': poll_id}  # no space/ underscore allowed in context key
    )

class PollOptionCreateView(CreateView):
    model = PollOption
    template_name = 'polloption/polloption_create.html'  # overwrite default 'polloption/polloption_form.html'
    form_class = PollOptionEditForm
    success_message = "Poll option created successfully"

    def get_initial(self):
        return {'poll_id': Poll.objects.get(pk=self.request.GET.get('poll_id'))}  # object associated with poll_id

    def get_context_data(self, **kwargs):  # pass extra context to template
        context = super().get_context_data(**kwargs)
        context["pollid"] = self.request.GET.get('poll_id')  # poll_id itself, context keys must not contain underscore
        return context

def pollOptionDeleteList(request):
    poll_id = str(request.GET.get('poll_id'))
    pollOptions = PollOption.objects.filter(poll_id=poll_id)

    return render(  # render request in template, and add context to template
        request, 
        template_name= "polloption/polloption_delete_list.html", 
        context = {'pollOptions': pollOptions, 'pollid': poll_id}
    )
    

class PollOptionDeleteView(DeleteView):
    model = PollOption
    # default template is 'polloption/polloption_confirm_delete.html'
    
    def get_success_url(self):
        poll_id = self.object.poll_id.id
        return reverse_lazy('poll-option-delete-list') + f"?poll_id={poll_id}"  # reverse cannot be used with success_url -> use reverse_lazy

    def get_context_data(self, **kwargs):  # pass extra context to template
        context = super().get_context_data(**kwargs)
        context["pollid"] = self.request.GET.get('poll_id')  # poll_id itself, context keys must not contain underscore
        return context
    
    

    