from django.shortcuts import render, redirect
from django.views.generic import CreateView, DeleteView
from django.contrib.auth.hashers import make_password
from django.urls import reverse, reverse_lazy
from passlib.handlers.django import django_pbkdf2_sha256
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from .forms import PollOptionEditFormSet, PollOptionEditForm
from .models import PollOption
from poll.models import Poll
from poll.views import getSavedPollPassword

def pollOptionEdit(request):
    poll_id = str(request.GET.get('poll_id'))
    pollOptions = PollOption.objects.filter(poll_id=poll_id)
    pollObject = Poll.objects.get(pk=poll_id)

    # password verification
    poll_password_hashed = pollObject.poll_password
    entered_password = getSavedPollPassword(request.session, poll_id)
    if pollObject.poll_password:
        if not entered_password:
            return redirect(reverse('poll-verify-password-redir-wpid') + "?id=" + str(poll_id) + "&next=" + reverse('poll-option-edit') + "&poll_id=" + str(poll_id))
        elif not django_pbkdf2_sha256.verify(entered_password, poll_password_hashed):
            messages.add_message(request, messages.ERROR, "Incorrect password")
            return redirect(reverse('poll-verify-password-redir-wpid') + "?id=" + str(poll_id) + "&next=" + reverse('poll-option-edit') + "&poll_id=" + str(poll_id))

    if request.method == 'POST':
        formset = PollOptionEditFormSet(request.POST, queryset = pollOptions)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.poll_id = pollObject
                instance.save()
            messages.add_message(request, messages.SUCCESS, "Poll options updated successfully")
            return redirect('poll-detail', pk=poll_id)
        messages.add_message(request, messages.ERROR, "Poll option updates failed due to invalid form input (all updates aborted)")
    else:  # GET request
        formset = PollOptionEditFormSet(queryset = pollOptions)
    
    if not pollOptions:
        template_name= "polloption/polloption_empty_queryset.html", 
    else:
        template_name= "polloption/polloption_edit.html",
    
    return render(  # render request in template, and add context to template
        request, 
        template_name= template_name, 
        context = {'formset': formset, 'pollid': poll_id}  # no space/ underscore allowed in context key
    )

def pollOptionCreate(request):
    poll_id = str(request.GET.get('poll_id'))
    pollObject = Poll.objects.get(pk=poll_id)

    # password verification
    poll_password_hashed = pollObject.poll_password
    entered_password = getSavedPollPassword(request.session, poll_id)
    if pollObject.poll_password:
        if not entered_password:
            return redirect(reverse('poll-verify-password-redir-wpid') + "?id=" + str(poll_id) + "&next=" + reverse('poll-option-create') + "&poll_id=" + str(poll_id))
        elif not django_pbkdf2_sha256.verify(entered_password, poll_password_hashed):
            messages.add_message(request, messages.ERROR, "Incorrect password")
            return redirect(reverse('poll-verify-password-redir-wpid') + "?id=" + str(poll_id) + "&next=" + reverse('poll-option-create') + "&poll_id=" + str(poll_id))

    if request.method == 'POST':
        form = PollOptionEditForm(request.POST, initial={'poll_id' : poll_id})
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Poll option created successfully")
            return redirect('poll-detail', pk=poll_id)
        messages.add_message(request, messages.ERROR, "Poll option creation failed due to invalid form input")
    else:  # GET request
        form = PollOptionEditForm(initial={'poll_id' : poll_id})

    return render(  # render request in template, and add context to template
        request, 
        template_name= 'polloption/polloption_create.html', 
        context = {'form': form, 'pollid': poll_id}  # no space/ underscore allowed in context key
    )

def pollOptionDeleteList(request):
    poll_id = str(request.GET.get('poll_id'))
    pollOptions = PollOption.objects.filter(poll_id=poll_id)

    if not pollOptions:
        template_name= "polloption/polloption_empty_queryset.html", 
    else:
        template_name= "polloption/polloption_delete_list.html", 
    
    return render(  # render request in template, and add context to template
        request, 
        template_name = template_name, 
        context = {'pollOptions': pollOptions, 'pollid': poll_id}
    )
    

class PollOptionDeleteView(SuccessMessageMixin, DeleteView):
    model = PollOption
    success_message = "Poll option deleted successfully"
    # default template is 'polloption/polloption_confirm_delete.html'
    
    def get_success_url(self):
        poll_id = self.object.poll_id.id
        return reverse_lazy('poll-option-delete-list') + f"?poll_id={poll_id}"  # reverse cannot be used with success_url -> use reverse_lazy

    def get_context_data(self, **kwargs):  # pass extra context to template
        context = super().get_context_data(**kwargs)
        context["pollid"] = self.request.GET.get('poll_id')  # poll_id itself, context keys must not contain underscore
        return context
    
    

    