from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Event, Attendee
from django.utils import timezone
from datetime import timedelta

# Create your tests here.

class EventAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.event = Event.objects.create(
            name="Test Event",
            location="Test Location",
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=2),
            max_capacity=2
        )

    def test_create_event(self):
        url = reverse('event-list-create')
        data = {
            "name": "New Event",
            "location": "New Location",
            "start_time": (timezone.now() + timedelta(days=3)).isoformat(),
            "end_time": (timezone.now() + timedelta(days=4)).isoformat(),
            "max_capacity": 10
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 2)

    def test_register_attendee(self):
        url = reverse('attendee-register', args=[self.event.id])
        data = {"name": "John Doe", "email": "john@example.com"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.event.attendees.count(), 1)

    def test_prevent_duplicate_registration(self):
        url = reverse('attendee-register', args=[self.event.id])
        data = {"name": "John Doe", "email": "john@example.com"}
        self.client.post(url, data, format='json')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already registered', str(response.data))

    def test_prevent_overbooking(self):
        url = reverse('attendee-register', args=[self.event.id])
        self.client.post(url, {"name": "A", "email": "a@example.com"}, format='json')
        self.client.post(url, {"name": "B", "email": "b@example.com"}, format='json')
        response = self.client.post(url, {"name": "C", "email": "c@example.com"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('max capacity', str(response.data))

    def test_attendee_list_pagination(self):
        url = reverse('attendee-register', args=[self.event.id])
        for i in range(15):
            self.client.post(url, {"name": f"User{i}", "email": f"user{i}@example.com"}, format='json')
        list_url = reverse('attendee-list', args=[self.event.id])
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 10)
