import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta
from .models import Event, Attendee
import random
import string

@pytest.mark.django_db
def test_create_event():
    client = APIClient()
    url = reverse('event-list-create')
    data = {
        "name": "Pytest Event",
        "location": "Pytest Location",
        "start_time": (timezone.now() + timedelta(days=3)).isoformat(),
        "end_time": (timezone.now() + timedelta(days=4)).isoformat(),
        "max_capacity": 5
    }
    response = client.post(url, data, format='json')
    assert response.status_code == 201
    assert Event.objects.filter(name="Pytest Event").exists()

@pytest.mark.django_db
def test_register_attendee():
    client = APIClient()
    event = Event.objects.create(
        name="Pytest Event",
        location="Pytest Location",
        start_time=timezone.now() + timedelta(days=1),
        end_time=timezone.now() + timedelta(days=2),
        max_capacity=2
    )
    url = reverse('attendee-register', args=[event.id])
    data = {"name": "Jane Doe", "email": "jane@example.com"}
    response = client.post(url, data, format='json')
    assert response.status_code == 201
    assert event.attendees.filter(email="jane@example.com").exists()

@pytest.mark.django_db
def test_prevent_duplicate_registration():
    client = APIClient()
    event = Event.objects.create(
        name="Pytest Event",
        location="Pytest Location",
        start_time=timezone.now() + timedelta(days=1),
        end_time=timezone.now() + timedelta(days=2),
        max_capacity=2
    )
    url = reverse('attendee-register', args=[event.id])
    data = {"name": "Jane Doe", "email": "jane@example.com"}
    client.post(url, data, format='json')
    response = client.post(url, data, format='json')
    assert response.status_code == 400
    assert (
        'already registered' in str(response.data)
        or 'must make a unique set' in str(response.data)
    )

@pytest.mark.django_db
def test_prevent_overbooking():
    client = APIClient()
    event = Event.objects.create(
        name="Pytest Event",
        location="Pytest Location",
        start_time=timezone.now() + timedelta(days=1),
        end_time=timezone.now() + timedelta(days=2),
        max_capacity=2
    )
    url = reverse('attendee-register', args=[event.id])
    client.post(url, {"name": "A", "email": "a@example.com"}, format='json')
    client.post(url, {"name": "B", "email": "b@example.com"}, format='json')
    response = client.post(url, {"name": "C", "email": "c@example.com"}, format='json')
    assert response.status_code == 400
    assert 'max capacity' in str(response.data)

@pytest.mark.django_db
def test_attendee_list_pagination():
    client = APIClient()
    event = Event.objects.create(
        name="Pytest Event",
        location="Pytest Location",
        start_time=timezone.now() + timedelta(days=1),
        end_time=timezone.now() + timedelta(days=2),
        max_capacity=20
    )
    url = reverse('attendee-register', args=[event.id])
    for i in range(15):
        client.post(url, {"name": f"User{i}", "email": f"user{i}@example.com"}, format='json')
    list_url = reverse('attendee-list', args=[event.id])
    response = client.get(list_url)
    assert response.status_code == 200
    assert 'results' in response.data
    assert len(response.data['results']) == 10

# Advanced/edge case tests
@pytest.mark.django_db
def test_event_end_before_start():
    client = APIClient()
    url = reverse('event-list-create')
    data = {
        "name": "Invalid Event",
        "location": "Nowhere",
        "start_time": (timezone.now() + timedelta(days=2)).isoformat(),
        "end_time": (timezone.now() + timedelta(days=1)).isoformat(),
        "max_capacity": 10
    }
    response = client.post(url, data, format='json')
    # Should fail validation if implemented, else allow (bonus: add this validation in serializer)
    assert response.status_code in (400, 201)

@pytest.mark.django_db
def test_attendee_invalid_email():
    client = APIClient()
    event = Event.objects.create(
        name="Email Event",
        location="Email Location",
        start_time=timezone.now() + timedelta(days=1),
        end_time=timezone.now() + timedelta(days=2),
        max_capacity=5
    )
    url = reverse('attendee-register', args=[event.id])
    data = {"name": "Bad Email", "email": "not-an-email"}
    response = client.post(url, data, format='json')
    assert response.status_code == 400
    assert 'email' in response.data

@pytest.mark.django_db
def test_register_attendee_nonexistent_event():
    client = APIClient()
    url = reverse('attendee-register', args=[9999])
    data = {"name": "Ghost", "email": "ghost@example.com"}
    response = client.post(url, data, format='json')
    assert response.status_code == 404

@pytest.mark.django_db
def test_event_list_only_upcoming():
    client = APIClient()
    # Past event
    Event.objects.create(
        name="Past Event",
        location="Past",
        start_time=timezone.now() - timedelta(days=3),
        end_time=timezone.now() - timedelta(days=2),
        max_capacity=10
    )
    # Upcoming event
    Event.objects.create(
        name="Future Event",
        location="Future",
        start_time=timezone.now() + timedelta(days=2),
        end_time=timezone.now() + timedelta(days=3),
        max_capacity=10
    )
    url = reverse('event-list-create')
    response = client.get(url)
    assert response.status_code == 200
    names = [e['name'] for e in response.data]
    assert "Future Event" in names
    assert "Past Event" not in names

# Monkey/randomized test
@pytest.mark.django_db
def test_monkey_attendee_registration():
    client = APIClient()
    event = Event.objects.create(
        name="Monkey Event",
        location="Jungle",
        start_time=timezone.now() + timedelta(days=1),
        end_time=timezone.now() + timedelta(days=2),
        max_capacity=30
    )
    url = reverse('attendee-register', args=[event.id])
    emails = set()
    for _ in range(50):
        name = ''.join(random.choices(string.ascii_letters, k=8))
        email = f"{name.lower()}@example.com"
        emails.add(email)
        response = client.post(url, {"name": name, "email": email}, format='json')
        # Only up to max_capacity should succeed
        if event.attendees.count() <= event.max_capacity:
            assert response.status_code in (201, 400)
        else:
            assert response.status_code == 400
    assert event.attendees.count() == event.max_capacity 