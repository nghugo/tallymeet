from django.shortcuts import render, redirect

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.db.models.query_utils import Q
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3

from .forms import (UserRegisterForm, RecapAuthenticationForm, ResendConfirmationForm, 
                    PasswordResetForm, SetPasswordForm, SetDisplayNameForm)
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
        messages.success(request, f'Dear {user.display_name}, please check your email inbox at {to_email} and click on \
    the activation link. This confirms your email address and completes the registration. You may have to wait a few minutes and check your spam folder.')
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


class RecapLoginView(auth_views.LoginView):  # Just the login view with Google reCAPTCHA added
    form_class = RecapAuthenticationForm


@login_required
def profile(request):
    return render(request, 'user/profile.html')


@login_required
def password_update(request):
    user = request.user
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been changed successfully")
            return redirect('user-profile')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = SetPasswordForm(user)
    return render(request, 'user/displayname_or_password_update.html', {'form': form, 'subheading': 'Password'})

@login_required
def displayname_update(request):
    user = request.user
    if request.method == 'POST':
        form = SetDisplayNameForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()        
            messages.success(request, "Your display name has been changed successfully")
            return redirect('user-profile')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    form = SetDisplayNameForm(instance=request.user)
    return render(request, 'user/displayname_or_password_update.html', {'form': form, 'subheading': 'Display Name'})


def passwordResetRequest(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            associated_user = User.objects.filter(Q(email=user_email)).first()
            if associated_user:
                subject = "Password Reset Request"
                message = render_to_string("user/template_reset_password.html", {
                    'name': associated_user.display_name,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    'token': account_activation_token.make_token(associated_user),
                    "protocol": 'https' if request.is_secure() else 'http'
                })
                email = EmailMessage(subject, message, to=[associated_user.email])
                if email.send():
                    messages.success(request,
                        """
                        We have emailed you instructions for setting your password, if an account exists with the email you entered. 
                        If you do not receive an email, please make sure you have entered the address you registered with. 
                        You may need to check your spam folder.
                        """
                    )
                else:
                    messages.error(request, "Problem sending reset password email (server problem)")

            return redirect('poll-home')

        for key, error in list(form.errors.items()):
            if key == 'captcha' and error[0] == 'This field is required.':
                messages.error(request, "You must pass the reCAPTCHA test")
                continue

    form = PasswordResetForm()
    return render(
        request=request, 
        template_name="user/password_reset_request.html", 
        context={"form": form}
        )


def passwordResetConfirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been set. You may log in now.")
                return redirect('user-login')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = SetPasswordForm(user)
        return render(request, 'user/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, "Link is expired")

    messages.error(request, 'Something went wrong, redirecting back to home page')
    return redirect("poll-home")
