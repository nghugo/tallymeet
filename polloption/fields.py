from datetime import timedelta
from django.db.models import DateTimeField

class DateTruncMixin:
    def truncate_date(self, dt):
        return dt
    def to_python(self, value):
        value = super().to_python(value)
        if value is not None:
            return self.truncate_date(value)
        return value

# create a DateTime field that truncates seconds
# https://stackoverflow.com/questions/69771533/django-models-datetimefield-how-to-store-the-value-without-seconds
class MinuteDateTimeField(DateTruncMixin, DateTimeField):
    def truncate_date(self, dt):
        return dt.replace(second=0, microsecond=0)