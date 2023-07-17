from django.contrib import admin
from .models import Poll, PollOption, PollOptionResponse, PollResponderXref

# Register your models here.
admin.site.register(Poll)
admin.site.register(PollOption)
admin.site.register(PollOptionResponse)
admin.site.register(PollResponderXref)