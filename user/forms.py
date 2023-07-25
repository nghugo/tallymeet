from django import forms
from user.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    display_name = forms.CharField()
    
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['display_name'].label = "Display Name"
        self.fields['password2'].label = "Confirm Password"

    class Meta:
        model = User
        fields = ['username', 'display_name', 'email', 'password1', 'password2']  
        # password1 password2 docs: https://docs.djangoproject.com/en/4.2/topics/auth/default/#django.contrib.auth.forms.BaseUserCreationForm 
    
    def clean(self):  # extra data validation
        cleaned_data = super().clean()

        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists")
    
        return cleaned_data