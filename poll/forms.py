from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from .models import Poll

class PollPasswordForm(forms.Form):
    poll_password = forms.CharField(max_length=200, widget=forms.PasswordInput)

class PollForm(ModelForm):
    class Meta:
        model = Poll
        fields = ["title", "description", "event_location", "poll_password"]
    
    title = forms.CharField()
    description = forms.Textarea()  # Textarea does not have label parameter, need to override in views.py
    event_location = forms.CharField(label="Event Location (optional)", required=False)
    poll_password = forms.CharField(label="Poll Password (optional)", widget=forms.PasswordInput(), help_text='Set and share a poll password so only your group can access this poll', required=False)
    poll_password_confirm = forms.CharField(label="Confirm Poll Password (if entered above)", widget=forms.PasswordInput(), help_text='Leave blank if a poll password has not been entered above', required=False)

    def clean(self):
        cleaned_data = super().clean()
        poll_password = cleaned_data.get("poll_password")
        poll_password_confirm = cleaned_data.get("poll_password_confirm")
        
        if poll_password or poll_password_confirm:
            if poll_password != poll_password_confirm:
                raise ValidationError('Poll passwords do not match')
    