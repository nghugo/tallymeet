from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from .models import PollOption
from poll.models import Poll


class PollOptionEditForm(ModelForm):
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

    def clean(self):  # data validation
        cleaned_data = super().clean()
        
        event_start_time = cleaned_data.get("event_start_time", None)
        event_end_time = cleaned_data.get("event_end_time", None)
        if event_start_time and event_end_time and event_start_time > event_end_time:
                raise ValidationError('Event must not end before start')
        
        return cleaned_data
    
        # also need to check for poll permission against poll_id here
        # TO IMPLEMENT CODE

# docs: https://docs.djangoproject.com/en/4.2/ref/forms/models/#modelformset-factory
PollOptionEditFormSet = forms.modelformset_factory(
    model = PollOption, 
    form = PollOptionEditForm, 
    exclude = None,
    extra = 0, 
    max_num = 20,
)

