import urllib.request
import urllib.parse
import urllib
from django.conf import settings
import json
import math
from random import random
from bisect import bisect_left
from geopy.distance import vincenty
#helper for making tripexpert API calls.
def tripexpert_api_venues(curr_lat, curr_long, venue_type, city):
    venue_type_dict = {'restaurant': '2', 'attraction':'3'}
    city_dict = {'new_york': '6'}

    base = "https://api.tripexpert.com/v1/venues?&order_by=distance"
    api = "&api_key=" + settings.TRIPEXPERT_API_KEY
    lat_long = '&latitude='+str(curr_lat)+'&longitude='+str(curr_long)
    venue_type = '&venue_type_id=' + venue_type_dict[venue_type]
    city = '&destination_id=' + city_dict[city]
    url = base + lat_long + venue_type + city + api
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp_json = urllib.request.urlopen(req).read().decode('utf-8')
    resp = json.loads(resp_json)
    return resp

def point_distance(x1,y1,x2,y2):
    return math.sqrt((x1 - x2)**2 + (y1-y2)**2)

#magic do not touch!!!! The success of this formula will determine the success of Spyglass
def calculate_score(factor, distance, tripexpert_score):
    #reverse the scaled distance scores so that small distances have a higher scaled score.
    scaled_distance = (distance - factor['min_distance']) / (factor['max_distance']-factor['min_distance'])
    scaled_tripexpert_score = (tripexpert_score - factor['min_score']) / (factor['max_score'] - factor['min_score'])
    return scaled_distance + 70*scaled_tripexpert_score

def create_route(info={'start_lat':40.7484, 'start_long':-73.98570000000001, 'end_lat':40.7484, 'end_long':-73.98570000000001}):
    #####starting options######
    curr_lat = info['start_lat']
    curr_long = info['start_long']
    end_lat = info['end_lat']
    end_long = info['end_long']
    remaining_distance = 10
    num_events = 5
    ###########################
    itinerary = []
    for i in range(num_events):
        #pick restaurant for lunch halfway through
        if i == num_events//2:
            venue_type = 'restaurant'
        else:
            venue_type = 'attraction'
        venues = tripexpert_api_venues(curr_lat, curr_long, venue_type, 'new_york')
        valid_venues = []
        factors = {
            'min_distance' : 999999,
            'max_distance' : 0,
            'min_score' : 100,
            'max_score' : 0,
        }

        #process all venues from api call
        for venue in venues['response']['venues']:
            #check for valid venue data
            api_attributes = ['distance', 'latitude', 'longitude', 'tripexpert_score']
            invalid_venue = False
            for attribute in api_attributes:
                if venue[attribute] is None:
                    invalid_venue=True
            if invalid_venue:
                break


            distance = float(venue['distance'])
            #end search if events are beyond search radius
            if distance > remaining_distance/2:
                break
            #skip if event is out of ellipse
            if distance + vincenty((curr_lat, curr_long), (end_lat, end_long)).miles > remaining_distance:
                continue
            #skip if event is already in itinerary
            if any([venue['id'] == x['id'] for x in itinerary]):
                continue
            #add venue to list of valid venues
            valid_venues.append(venue)

############ modify factors here: ####################################
            distance = 1/((distance+.1)**2)
            venue_score = math.exp(venue['tripexpert_score'])

            venue['~distance'] = distance
            venue['~tripexpert_score'] = venue_score
######################################################################

            #update max and mins
            if distance > factors['max_distance']:
                factors['max_distance'] = distance
            if distance < factors['min_distance']:
                factors['min_distance'] = distance
            if venue_score > factors['max_score']:
                factors['max_score'] = venue_score
            if venue_score < factors['min_score']:
                factors['min_score'] = venue_score

        #calculate each score and setup array of events and scores for 'random' picking
        venue_score_picker = []
        cum_score = 0
        for index, venue in enumerate(valid_venues):
            venue_score = calculate_score(factors, venue['~distance'], venue['~tripexpert_score'])
            cum_score += venue_score
            venue_score_picker.append(cum_score)
        #generate random number and binary search to find random event until a non-dupicate one is found.
        random_num = random() * cum_score
        index = bisect_left(venue_score_picker, random_num)
        selected_venue = valid_venues[index]
        #update itinerary and stats
        itinerary.append(selected_venue)
        curr_lat = selected_venue['latitude']
        curr_long = selected_venue['longitude']
        remaining_distance -= selected_venue['distance']
    return itinerary
    #TODO check for edge cases like no events found
