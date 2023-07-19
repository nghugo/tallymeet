from django.db import models
from poll.models import Poll

class PollOption(models.Model):
    poll_id = models.ForeignKey(Poll, on_delete=models.CASCADE)
    event_start_time = models.DateTimeField()
    event_end_time = models.DateTimeField()

    def __str__(self):
        return (self.poll_id, (self.event_start_time, self.event_end_time))