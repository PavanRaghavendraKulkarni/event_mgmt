from rest_framework import serializers
from .models import Event, Attendee
from django.utils import timezone
from .services import to_ist, to_utc

class EventSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()

    class Meta:
        model = Event
        fields = ['id', 'name', 'location', 'start_time', 'end_time', 'max_capacity']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['start_time'] = to_ist(instance.start_time).isoformat() if instance.start_time else None
        rep['end_time'] = to_ist(instance.end_time).isoformat() if instance.end_time else None
        return rep

    def validate_start_time(self, value):
        # Assume input is in IST, convert to UTC for storage
        return to_utc(value)

    def validate_end_time(self, value):
        # Assume input is in IST, convert to UTC for storage
        return to_utc(value)

class AttendeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendee
        fields = ['id', 'name', 'email', 'event', 'registered_at']
        read_only_fields = ['registered_at']

    def validate(self, data):
        event = data.get('event')
        email = data.get('email')
        if Attendee.objects.filter(event=event, email=email).exists():
            raise serializers.ValidationError('This email is already registered for this event.')
        if event.attendees.count() >= event.max_capacity:
            raise serializers.ValidationError('Event is already at max capacity.')
        return data 