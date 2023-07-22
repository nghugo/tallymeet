from django import forms
from django.forms import ModelForm
from django.forms.models import BaseModelFormSet, BaseInlineFormSet
from django.core.exceptions import ValidationError
from .models import PollOption
from poll.models import Poll

class PollOptionEditForm(ModelForm):
    def __init__(self, *args, **kwargs):
        """By default, modelformset_facotry alwasy sustains the old data (from DB)
        https://stackoverflow.com/questions/29472751/django-modelformset-factory-sustains-the-previously-submitted-data-even-after-su """
        
        # self.poll_id = kwargs.pop('poll_id')
        super(PollOptionEditForm, self).__init__(*args, **kwargs)
        # self.fields['poll_id'].queryset = PollOption.objects.filter(id=self.poll_id)
        
        # self.queryset = PollOption.objects.filter(id=2)
        self.queryset = PollOption.objects.none()


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


    # widget -> Hide from the form ; # disabled -> unchangable field
    # poll_id = forms.ModelChoiceField(queryset = queryset, disabled=True, widget = forms.HiddenInput())
    
    # *************************************************
    # TO IMPLEMENT QUERYSET FILTERING
    # poll_id = forms.ModelChoiceField(queryset = Poll.objects.filter(id=2), disabled=True)
    poll_id = forms.ModelChoiceField(queryset = Poll.objects.all(), disabled=True)
    
    

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

# # inlineformset_factory takes care of queryset https://stackoverflow.com/questions/1988968/django-formset-how-to-update-an-object
# PollOptionEditFormSet = forms.inlineformset_factory(
#     parent_model = Poll, 
#     model = PollOption, 
#     form = PollOptionEditForm, 
#     exclude = None,
#     extra = 1,
#     can_delete = False,
# )

# class PollOptionEditFormSet(BaseInlineFormSet):
# # class PollOptionEditFormSet(BaseModelFormSet):
#      def __init__(self, *args, **kwargs):
#           super(PollOptionEditFormSet, self).__init__(*args, **kwargs)
#           self.queryset = Poll.objects.none()
#           self.model = PollOption
#           # form, exclude, extra, max_num missing
