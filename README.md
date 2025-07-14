# Event Management System API

A mini event management backend built with Django, Django REST Framework, and SQLite. Supports event creation, attendee registration, pagination, timezone handling, and admin panel.

## Features
- Create and list events
- Register attendees (no duplicates, no overbooking)
- List attendees with pagination
- Timezone management (all times in IST for API, stored as UTC)
- Django admin panel
- Swagger/OpenAPI docs
- Unit tests

## Setup Instructions

1. **Clone the repo or unzip the folder**
2. **Install dependencies:**
   ```sh
   pip3 install -r requirements.txt
   ```
3. **Apply migrations:**
   ```sh
   python3 manage.py migrate
   ```
4. **Create a superuser (for admin panel):**
   ```sh
   python3 manage.py createsuperuser
   ```
5. **Run the server:**
   ```sh
   python3 manage.py runserver
   ```
6. **Access:**
   - API: http://127.0.0.1:8000/api/
   - Admin: http://127.0.0.1:8000/admin/
   - Swagger/OpenAPI: http://127.0.0.1:8000/openapi/

## API Endpoints

### Create Event
```
POST /api/events/
Content-Type: application/json
{
  "name": "My Event",
  "location": "Mumbai",
  "start_time": "2024-07-15T10:00:00+05:30",  # IST
  "end_time": "2024-07-15T12:00:00+05:30",    # IST
  "max_capacity": 100
}
```

### List Upcoming Events
```
GET /api/events/
```

### Register Attendee
```
POST /api/events/{event_id}/register/
Content-Type: application/json
{
  "name": "Alice",
  "email": "alice@example.com"
}
```

### List Attendees (with pagination)
```
GET /api/events/{event_id}/attendees/?page=1&page_size=10
```

## Timezone Handling
- All API input/output datetimes are in IST (`+05:30`).
- Internally, times are stored in UTC for consistency.

## Running Tests
```
python3 manage.py test events
```

## Assumptions
- Event times are always provided and returned in IST.
- Duplicate attendee emails per event are not allowed.
- Overbooking is prevented at registration.

---

For any questions, see the code or contact the author. 