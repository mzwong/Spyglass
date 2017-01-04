from django.shortcuts import render
import urllib.request
import urllib.parse
import urllib
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from .route_generate import create_route
import json

# Create your views here.
def index(request):
    return render(request, 'spyglassapp/index.html')

def select_city(request):
    return render(request, 'spyglassapp/select_city.html')

def new_york_city_venues(request):
    req = urllib.request.Request("https://api.tripexpert.com/v1/venues?destination_id=6&api_key=" + settings.TRIPEXPERT_API_KEY, headers={'User-Agent': 'Mozilla/5.0'})
    resp_json = urllib.request.urlopen(req).read().decode('utf-8')
    resp = json.loads(resp_json)
    context = {'venues': resp['response']['venues']}
    return render(request, 'spyglassapp/venue_list.html', context)

def city_options(request, city):
    return HttpResponse("city options - TBD")

def route(request, city):
    return HttpResponse(create_route())
