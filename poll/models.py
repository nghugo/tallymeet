from django.db import models
from django.utils import timezone
from user.models import User
from django.urls import reverse

class Poll(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    event_location = models.CharField(max_length=4096, blank=True, null=True)
    poll_password = models.CharField(max_length=255, blank=True, null=True)  # hashed
    date_created = models.DateTimeField(default=timezone.now)
    owner_id = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)  # nullable, since Polls do not need an owner

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('poll-detail', kwargs={'pk': self.pk})  # return full URL as string

class PollResponderXref(models.Model):
    responder_user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    poll_id = models.ForeignKey(Poll, on_delete=models.CASCADE)
    
    def __str__(self):
        return ''.join([str(self.responder_user_id), str(self.poll_id)])


