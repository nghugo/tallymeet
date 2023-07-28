from django.db import models
from django.urls import reverse
from user.models import User

from poll.models import Poll

from .fields import MinuteDateTimeField

class PollOption(models.Model):
    poll_id = models.ForeignKey(Poll, on_delete=models.CASCADE)
    event_start_time = MinuteDateTimeField()
    event_end_time = MinuteDateTimeField()

    def __str__(self):
        return ''.join([str(self.poll_id), str(self.event_start_time), str(self.event_end_time)])
    
    def get_absolute_url(self):
        return reverse('poll-detail', kwargs={'pk': self.poll_id.id})  # return full URL as string

class PollOptionResponse(models.Model):
    PREFER = "P"
    YES = "Y"
    NO = "N"
    RESPONSE_CHOICES = [(PREFER, "Prefer"), (YES, "Yes"), (NO, "No")]

    poll_option_id = models.ForeignKey(PollOption, on_delete=models.CASCADE)
    responder_user_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    responder_nonuser_id = models.CharField(max_length=255, null=True, blank=True)
    responder_name = models.CharField(max_length=255)
    response = models.CharField(max_length=1, choices=RESPONSE_CHOICES)

    def __str__(self):
        return ''.join([str(self.responder_user_id), str(self.poll_option_id)])