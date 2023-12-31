from django import forms
from django.contrib.auth.forms import (UserCreationForm, AuthenticationForm,
                                       PasswordResetForm, SetPasswordForm)
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from django.forms import ModelForm, Form

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3

from user.models import User

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(max_length=320)
    display_name = forms.CharField(max_length=255)
    captcha = ReCaptchaField(widget=ReCaptchaV3(attrs={'required_score':0.4}), label="")
        
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['display_name'].label = "Display Name"
        self.fields['password2'].label = "Confirm Password"

    class Meta:
        model = User
        fields = ['email', 'display_name', 'password1', 'password2']  
        # password1 password2 docs: https://docs.djangoproject.com/en/4.2/topics/auth/default/#django.contrib.auth.forms.BaseUserCreationForm 
    
    def clean(self):  # extra data validation
        cleaned_data = super().clean()

        if "email" in self.cleaned_data:
            email = self.cleaned_data["email"]
            if User.objects.filter(email=email).exists():
                raise ValidationError("A user with this email already exists")
        
        return cleaned_data


class RecapAuthenticationForm(AuthenticationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV3(attrs={'required_score':0.4}), label="")

class ResendConfirmationForm(forms.Form):
    email = forms.EmailField()
    captcha = ReCaptchaField(widget=ReCaptchaV3(attrs={'required_score':0.4}), label="")

class PasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)

    captcha = ReCaptchaField(widget=ReCaptchaV3(attrs={'required_score':0.4}), label="")

class SetPasswordForm(SetPasswordForm):
    class Meta:
        model = User
        fields = ['new_password1', 'new_password2']

    captcha = ReCaptchaField(widget=ReCaptchaV3(attrs={'required_score':0.4}), label="")

class SetDisplayNameForm(ModelForm):
    display_name = forms.CharField(max_length=255)
    class Meta:
        model = User
        fields = ['display_name']

class UserDeleteRequestForm(Form):
    captcha = ReCaptchaField(widget=ReCaptchaV3(attrs={'required_score':0.4}), label="")

class UserDeleteConfirmForm(Form):
    password = forms.CharField(label="Account Password", widget=forms.PasswordInput(), help_text='Please enter your account password to confirm account deletion')
    captcha = ReCaptchaField(widget=ReCaptchaV3(attrs={'required_score':0.4}), label="")

