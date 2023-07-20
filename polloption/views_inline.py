import datetime

from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse, reverse_lazy
from django.contrib import messages

from .models import PollOption
from poll.models import Poll
from .forms import PollOptionCreateForm, PollOptionCreateInlineFormSet
from poll.forms import PollCreateForm

class PollOptionCreateView(CreateView):
    form_class = PollOptionCreateForm
    template_name = 'polloption/polloption_create.html'  # override default polloption/polloption_form.html'
    
    def get_initial(self):
        return {'poll_id': Poll.objects.get(pk=self.request.GET.get('poll_id'))}

    def get_context_data(self, **kwargs):  # pass formset as extra context to template
        context = super().get_context_data(**kwargs)
        context["formset"] = PollOptionCreateInlineFormSet()
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        poll_option_formset = PollOptionCreateInlineFormSet(self.request.POST)
        if form.is_valid() and poll_option_formset.is_valid():
            return self.form_valid(form, poll_option_formset)
        else:
            return self.form_invalid(form, poll_option_formset)
    
    def form_valid(self, form, poll_option_formset):
        self.object = form.save(commit=False)
        self.object.save()
        # saving pollOption Instances
        poll_options = poll_option_formset.save(commit=False)
        for option in poll_options:
            option.poll = self.object
            option.save()
        # print("**************** key, val received in POST request as:")  # DEBUG
        # for key, val in self.request.POST.items():
        #     print(key, val)
        return super().form_valid(form)
        # return redirect(reverse("poll:poll_list"))
        
    
    def form_invalid(self, form, poll_option_formset):
        return self.render_to_response(
            self.get_context_data(form=form,
                                  poll_option_formset=poll_option_formset
                                  )
        )

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

       # def post(self, request, *args, **kwargs):
    #     formset = PollOptionCreateFormSet(request.POST)
    #     # optionform = PollOptionCreateForm(data=request.POST)
    #     # if formset.is_valid() and optionform.is_valid():
    #     return self.form_valid(formset)# , optionform