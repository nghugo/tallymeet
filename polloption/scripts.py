from datetime import datetime
from .models import PollOption
from poll.models import Poll

def addPollOption(poll_id):
    poll_option = PollOption(
        poll_id = Poll.objects.get(pk=poll_id),
        event_start_time = datetime.min,
        event_end_time = datetime.min
    )
    poll_option.save()

