from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models


class EventType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_event_types')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=50)
    date_and_time = models.DateTimeField()
    location = models.CharField(max_length=100)
    description = models.TextField()
    max_participants = models.PositiveIntegerField(null=True, blank=True)
    event_type = models.ForeignKey(EventType, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


def event_image_upload_to(instance, filename):
    return f'event_images/{instance.event.name}/{filename}'


class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=event_image_upload_to, null=True, blank=True)

    def __str__(self):
        return f"Image for {self.event.name}"


class Participant(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    first_name = models.CharField(max_length=20, validators=[RegexValidator(r'^[a-zA-Z]+$')])
    last_name = models.CharField(max_length=20, validators=[RegexValidator(r'^[a-zA-Z]+$')])
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True, default='default/img.png')
    email = models.EmailField()
    phone_number = models.CharField(max_length=15, validators=[RegexValidator(r'^\+?1?\d{9,15}$')])
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('email', 'event'),)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
