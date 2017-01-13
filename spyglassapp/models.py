from django.db import models
from django.contrib.auth.models import User, Group

# Create your models here.

class Itinerary(models.Model):
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=200, unique=True)
    location = models.CharField(max_length=200)
    start_latitude = models.FloatField()
    start_longitude = models.FloatField()
    end_latitude = models.FloatField()
    end_longitude = models.FloatField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    cost = models.IntegerField()


class Event(models.Model):
    itinerary = models.ForeignKey(Itinerary)
    service_id = models.IntegerField()
    service_name = models.CharField(max_length=200)
    time = models.DateTimeField()
    location = models.CharField(max_length=200)



