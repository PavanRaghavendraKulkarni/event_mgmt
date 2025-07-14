from django.db import models
from django.utils import timezone

class Event(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    max_capacity = models.PositiveIntegerField()
    timezone = models.CharField(max_length=64, default='Asia/Kolkata')

    def __str__(self):
        return f"{self.name} @ {self.location} ({self.start_time})"

class Attendee(models.Model):
    event = models.ForeignKey(Event, related_name='attendees', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    registered_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('event', 'email')

    def __str__(self):
        return f"{self.name} <{self.email}> for {self.event.name}"
