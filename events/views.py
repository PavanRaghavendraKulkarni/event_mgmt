from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Event, Attendee
from .serializers import EventSerializer, AttendeeSerializer
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination

# Create your views here.

class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_queryset(self):
        now = timezone.now()
        return Event.objects.filter(start_time__gte=now).order_by('start_time')

class AttendeeRegisterView(APIView):
    def post(self, request, event_id):
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return Response({'detail': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data.copy()
        data['event'] = event.id
        serializer = AttendeeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AttendeePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class AttendeeListView(generics.ListAPIView):
    serializer_class = AttendeeSerializer
    pagination_class = AttendeePagination

    def get_queryset(self):
        event_id = self.kwargs['event_id']
        return Attendee.objects.filter(event_id=event_id).order_by('-registered_at')
