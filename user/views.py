from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import SetPasswordForm

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3

from .forms import UserRegisterForm, RecapAuthenticationForm, ResendConfirmationForm
from .tokens import account_activation_token
from .models import User

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


def activateEmail(request, user, to_email):  # to_email -> address of recipent ; email -> our email object to send
    mail_subject = 'Activate Your Tallymeet User Account'
    message = render_to_string('user/template_activate_account.html', {
        'name': user.display_name,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear {user.display_name}, please go to the inbox of your email {to_email} and click on \
    the activation link to confirm your email address and complete the registration. You may have to check your spam folder.')
    else:
        messages.error(request, f'Problem sending confirmation email, please check if you typed it correctly.')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Thank you for your email confirmation. You may log in now.')
        return redirect('user-login')
    else:
        messages.error(request, 'Activation link is invalid!')
    return redirect('poll-home')

def resend_activation(request):
    if request.method == 'POST':
        form = ResendConfirmationForm(request.POST)
        if form.is_valid():

            email = request.POST.get('email')
            user = User.objects.filter(email=email).first()  # return None if not found
            if user and not user.is_active:
                activateEmail(request, user, form.cleaned_data.get('email'))
                
            messages.add_message(request, messages.SUCCESS, f"The activation email has been re-sent, if your provided email {form.cleaned_data.get('email')} is tied to an inactive Tallymeet account.")
            return redirect('user-login')
        messages.add_message(request, messages.ERROR, f"Cannot process email {form.cleaned_data.get('email')}, please check if you typed it correctly.")
    else:  # GET request
        form = ResendConfirmationForm()

    return render(  # render request in template, and add context to template
        request, 
        template_name= 'user/resend_confirmation.html', 
        context = {'form': form}
    )


@login_required
def profile(request):
    return render(request, 'user/profile.html')

class RecapLoginView(auth_views.LoginView):
    form_class = RecapAuthenticationForm


@login_required
def password_update(request):
    user = request.user
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been changed")
            return redirect('user-login')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = SetPasswordForm(user)
    return render(request, 'user/password_update.html', {'form': form})