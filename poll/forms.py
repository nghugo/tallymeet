from django import forms

class PollPasswordForm(forms.Form):
    poll_password = forms.CharField(max_length=200)
    