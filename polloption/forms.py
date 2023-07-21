from django import forms
from django.forms import ModelForm, BaseFormSet, Form
from django.core.exceptions import ValidationError
from .models import PollOption
from poll.models import Poll


class PollOptionCreateForm(ModelForm):

    class Meta:
        model = PollOption
        fields = ["poll_id", "event_start_time", "event_end_time"]
        # poll_id is a hiddenfield to be filled in using poll_id in url
        # to prevent tampering, also need to check for permission (against poll password of poll_id)        

        # temp disable DEBUG
        widgets = {
            'event_start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'event_end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


    queryset = Poll.objects.all()  # MODIFY TO CONTROL POLL PASSWORD BASED PERMISSIONS
    poll_id = forms.ModelChoiceField(queryset = queryset, disabled=True, widget = forms.HiddenInput())
    # widget -> Hide from the form ; # disabled -> unchangable field

    # temp disable DEBUG
    # def clean(self):
    #     cleaned_data = super().clean()
    #     print("**************** key, val cleaned as:")
    #     for key, val in cleaned_data.items():
    #         print(key, val)
    #     return super().clean()

    #     event_start_time = cleaned_data.get("event_start_time")
    #     event_end_time = cleaned_data.get("event_end_time")
        
    #     print("***************************")
    #     for key, val in cleaned_data.items():
    #         print(f"{key} received as {val}")
        
    #     if not (event_start_time and event_end_time):
    #         raise ValidationError('Please enter both event start and end times')

    #     if event_start_time > event_end_time:
    #         raise ValidationError('Event must start before end')
        
        # also need to check for poll permission against poll_id here
        # TO IMPLEMENT CODE

# docs: https://docs.djangoproject.com/en/4.2/ref/forms/models/#modelformset-factory
PollOptionCreateFormSet = forms.modelformset_factory(
    model = PollOption, 
    form = PollOptionCreateForm, 
    exclude = None,
    extra = 0, 
    max_num = 5,
)

# using initial data with formset https://docs.djangoproject.com/en/4.2/topics/forms/formsets/#using-initial-data-with-a-formset