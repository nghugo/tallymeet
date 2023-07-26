from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3

from .models import Poll

class PollPasswordForm(forms.Form):
    poll_password = forms.CharField(max_length=200, widget=forms.PasswordInput)
    captcha = ReCaptchaField(widget=ReCaptchaV3(attrs={'required_score':0.85}), label="")


class PollCreateForm(ModelForm):
    class Meta:
        model = Poll
        fields = ["title", "description", "event_location", "poll_password"]
    
    title = forms.CharField()
    description = forms.Textarea()  # Textarea does not have label parameter, need to override in views.py
    event_location = forms.CharField(label="Event Location (optional)", required=False, help_text='If your event is video-based, consider putting the link here')
    poll_password = forms.CharField(label="Poll Password (optional)", widget=forms.PasswordInput(), help_text='Set and share a poll password so only your group can access this poll', required=False)
    poll_password_confirm = forms.CharField(label="Confirm Poll Password (if entered above)", widget=forms.PasswordInput(), help_text='Please leave blank if a poll password has not been entered above', required=False)
    captcha = ReCaptchaField(widget=ReCaptchaV3(attrs={'required_score':0.85}), label="")

    def clean(self):
        cleaned_data = super().clean()
        poll_password = cleaned_data.get("poll_password")
        poll_password_confirm = cleaned_data.get("poll_password_confirm")
        
        if poll_password or poll_password_confirm:
            if poll_password != poll_password_confirm:
                raise ValidationError('Poll passwords do not match')


class PollUpdatePasswordForm(ModelForm):
    class Meta:
        model = Poll
        fields = ["poll_password"]
    
    poll_password = forms.CharField(label="New Poll Password (optional)", widget=forms.PasswordInput(), help_text='Update the poll password so only your group can access this poll', required=False)
    poll_password_confirm = forms.CharField(label="Confirm New Poll Password (if entered above)", widget=forms.PasswordInput(), help_text='Please leave blank if a poll password has not been entered above', required=False)

    def clean(self):
        cleaned_data = super().clean()
        poll_password = cleaned_data.get("poll_password")
        poll_password_confirm = cleaned_data.get("poll_password_confirm")
        
        if poll_password or poll_password_confirm:
            if poll_password != poll_password_confirm:
                raise ValidationError('New poll passwords do not match')

        

    