from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from .models import PollOption
from poll.models import Poll


class PollOptionCreateForm(ModelForm):            
    class Meta:
        model = PollOption
        fields = ["poll_id", "event_start_time", "event_end_time"]
        # poll_id is a hiddenfield, we will fill it in using the session object
        # to prevent tampering, also check for permission (against poll password of poll_id)        

        widgets = {
            'event_start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'event_end_time':  forms.DateTimeInput(attrs={'type': 'datetime-local'})     
        }
    
    queryset = Poll.objects.all()  # MODIFY TO CONTROL POLL PASSWORD BASED PERMISSIONS

    poll_id = forms.ModelChoiceField(queryset = queryset)
    # poll_id = forms.ModelChoiceField(queryset = queryset, widget = forms.HiddenInput())

    def clean(self):
        cleaned_data = super().clean()
        event_start_time = cleaned_data.get("event_start_time")
        event_end_time = cleaned_data.get("event_end_time")
        
        if not (event_start_time and event_end_time):
            raise ValidationError('Please enter both event start time and event end time')

        if event_start_time > event_end_time:
            raise ValidationError('Event must start before end')
        
        # also need to check for poll permission against poll_id here
        # TO IMPLEMENT CODE

# Use a formset to repeat PollOptionCreateForm

PollOptionCreateFormSet = forms.formset_factory(PollOptionCreateForm, extra=2)
# using initial data with formset https://docs.djangoproject.com/en/4.2/topics/forms/formsets/#using-initial-data-with-a-formset