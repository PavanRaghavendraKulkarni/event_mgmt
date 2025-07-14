from django.urls import path
from .views import EventListCreateView, AttendeeRegisterView, AttendeeListView, EventUpdateView

urlpatterns = [
    path('events/', EventListCreateView.as_view(), name='event-list-create'),
    path('events/<int:event_id>/register/', AttendeeRegisterView.as_view(), name='attendee-register'),
    path('events/<int:event_id>/attendees/', AttendeeListView.as_view(), name='attendee-list'),
    path('events/<int:pk>/update/', EventUpdateView.as_view(), name='event-update'),
] 