from rest_framework import serializers
from .models import Event, Attendee
from django.utils import timezone
from .services import to_ist, to_utc
from django.db import IntegrityError
from django.db.utils import IntegrityError as DBIntegrityError

class EventSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()

    class Meta:
        model = Event
        fields = ['id', 'name', 'location', 'start_time', 'end_time', 'max_capacity', 'timezone']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        tz = instance.timezone if hasattr(instance, 'timezone') else 'Asia/Kolkata'
        from .services import to_local
        rep['start_time'] = to_local(instance.start_time, tz).isoformat() if instance.start_time else None
        rep['end_time'] = to_local(instance.end_time, tz).isoformat() if instance.end_time else None
        return rep

    def validate_start_time(self, value):
        tz = self.initial_data.get('timezone', 'Asia/Kolkata')
        from .services import to_utc_from_local
        return to_utc_from_local(value, tz)

    def validate_end_time(self, value):
        tz = self.initial_data.get('timezone', 'Asia/Kolkata')
        from .services import to_utc_from_local
        return to_utc_from_local(value, tz)

    def update(self, instance, validated_data):
        old_timezone = instance.timezone
        new_timezone = validated_data.get('timezone', old_timezone)
        if new_timezone != old_timezone:
            import pytz
            from django.utils import timezone as dj_timezone
            old_tz = pytz.timezone(old_timezone)
            new_tz = pytz.timezone(new_timezone)
            # Convert from UTC to old timezone, then to new timezone, then back to UTC
            for field in ['start_time', 'end_time']:
                dt = getattr(instance, field)
                if dt:
                    # Convert UTC -> old_tz
                    dt_old = dt.astimezone(old_tz)
                    # Convert old_tz -> new_tz
                    dt_new = dt_old.astimezone(new_tz)
                    # Store as UTC
                    dt_utc = dt_new.astimezone(pytz.UTC)
                    validated_data[field] = dt_utc
        return super().update(instance, validated_data)

class AttendeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendee
        fields = ['id', 'name', 'email', 'event', 'registered_at']
        read_only_fields = ['registered_at']

    def validate_email(self, value):
        event = self.initial_data.get('event')
        if event and Attendee.objects.filter(event=event, email=value).exists():
            raise serializers.ValidationError('This email is already registered for this event.')
        return value

    def validate(self, data):
        event = data.get('event')
        if event.attendees.count() >= event.max_capacity:
            raise serializers.ValidationError('Event is already at max capacity.')
        return data

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except (IntegrityError, DBIntegrityError):
            raise serializers.ValidationError({'email': 'This email is already registered for this event.'}) 