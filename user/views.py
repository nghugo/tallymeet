from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # user cannot log in until email is verified
            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))
            return redirect('user-login')
    else:
        form = UserRegisterForm()
    return render(request, 'user/register.html', {'form': form})


def activateEmail(request, user, email):
    messages.success(request, f'Dear {user}, please go to you the inbox of your email {email} and click on \
    received activation link to confirm and complete the registration. Note: Check your spam folder.')


@login_required
def profile(request):
    return render(request, 'user/profile.html')