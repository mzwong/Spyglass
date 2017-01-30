from django.shortcuts import render, redirect
import urllib.request
import urllib.parse
import urllib
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.conf import settings
from .route_generate import create_route
import json
from .forms import *
from django.core.urlresolvers import reverse
#import googlemaps

# Create your views here.

#helper for making tripexpert API calls
def tripexpert_venue_info(venue_id):
    req = urllib.request.Request("https://api.tripexpert.com/v1/venues/" + venue_id + "?api_key=" + settings.TRIPEXPERT_API_KEY, headers={'User-Agent': 'Mozilla/5.0'})
    resp_json = urllib.request.urlopen(req).read().decode('utf-8')
    resp = json.loads(resp_json)
    return resp['response']['venue'][0]


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
    if request.method == 'GET':
        options_form = OptionsForm()
        return render(request, 'spyglassapp/options.html', {'form': options_form})
    else:
        options_form = OptionsForm(request.POST)
        if not options_form.is_valid():
            return render(request, 'spyglassapp/options.html', {'form': options_form})

        options_form.save(commit=False)
        start = options_form.cleaned_data['starting_position']
        end = options_form.cleaned_data['ending_position']
        info = {}
        info['start_lat'] = float(start[0])
        info['start_long'] = float(start[1])
        info['end_lat'] = float(end[0])
        info['end_long'] = float(end[1])
        info['cost'] = int(options_form.cleaned_data['cost'])
        request.session['options'] = info
        return redirect('route', city=city)

#info will be recieved from the city options form
def route(request, city):
    options = request.session['options']
    itinerary = create_route(options)
    starting_point = [options['start_lat'], options['start_long']]
    ending_point = [options['end_lat'], options['end_long']]
    locations = [starting_point]
    for i in itinerary:
        venue_info = tripexpert_venue_info(i['id'])
        i['address'] = venue_info['address']
        i['phone'] = venue_info['telephone']
        i['website'] = venue_info['website']
        i['reviews'] = venue_info['reviews']
        #add coordinates of events to locations array
        point = [float(i['latitude']), float(i['longitude'])]
        locations.append(point)
    locations.append(ending_point)
    context = {'itin': itinerary, 'coordinates': locations}
    return render(request, 'spyglassapp/route.html', context)

#def directions(request):
#    gmaps = googlemaps.Client(key='AIzaSyBD4Y4-37CkPsNRzX8V5nbOn74wDB37vdE')
#    direction = gmaps.directions("Disneyland", "Universal Studios Hollywood", mode="transit")
#    response = json.dumps(direction)
#    geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')
#    return HttpResponse(response['status'])
