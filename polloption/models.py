from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

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
    responder_id = models.ForeignKey(User, on_delete=models.CASCADE)
    poll_option_id = models.ForeignKey(PollOption, on_delete=models.CASCADE)
    response = models.CharField(max_length=8)

    def __str__(self):
        return ''.join([str(self.responder_id), str(self.poll_option_id)])