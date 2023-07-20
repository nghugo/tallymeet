from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.core.exceptions import ValidationError

from .models import PollOption
from poll.models import Poll

class PollOptionCreateForm(ModelForm):
    class Meta:
        model = PollOption
        # fields = ["poll_id", "event_start_time", "event_end_time"]
        fields = ["event_start_time", "event_end_time"]
        # poll_id -> hidden field, filled url param, and check for permission (against poll_password)

        # temp disable DEBUG
        # widgets = {
        #     # 'event_start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        #     'event_end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        # }

# eg https://techincent.com/explained-django-inline-formset-factory-with-example/
PollOptionCreateInlineFormSet = inlineformset_factory(
    parent_model = Poll,
    model = PollOption, 
    form = PollOptionCreateForm, 
    extra = 0, 
    max_num = 10,
)

# using initial data with formset https://docs.djangoproject.com/en/4.2/topics/forms/formsets/#using-initial-data-with-a-formset