from django.contrib import admin
from .models import Event, Attendee

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "start_time", "end_time", "max_capacity")
    search_fields = ("name", "location")
    list_filter = ("start_time", "location")

@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "event", "registered_at")
    search_fields = ("name", "email", "event__name")
    list_filter = ("event",)
