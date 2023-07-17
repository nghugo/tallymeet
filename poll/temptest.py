from django.contrib.auth.hashers import make_password
from passlib.handlers.django import django_pbkdf2_sha256

password = 'nicepassword2'
django_hash = 'pbkdf2_sha256$600000$NLDZOCQhj3sMyMpXipFyLr$phI4H2gS+G2N5s9jJ0bO33r9p6Qm9NBzwrdwQRuHvm4='
is_verified = django_pbkdf2_sha256.verify(password, django_hash)

if is_verified:
  print('Correct!!')
else:
  print('nope...')