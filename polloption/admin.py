from django.contrib import admin
from .models import PollOption, PollOptionResponse

# Register your models here.
admin.site.register(PollOption)
admin.site.register(PollOptionResponse)