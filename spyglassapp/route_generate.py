import urllib.request
import urllib.parse
import urllib
from django.conf import settings
import json
import math
from random import random
from bisect import bisect_left
from geopy.distance import vincenty
#helper for making tripexpert API calls
def tripexpert_api_helper(endpoint):
    req = urllib.request.Request("https://api.tripexpert.com/v1/" + endpoint + "&api_key=" + settings.TRIPEXPERT_API_KEY, headers={'User-Agent': 'Mozilla/5.0'})
    resp_json = urllib.request.urlopen(req).read().decode('utf-8')
    resp = json.loads(resp_json)
    return resp

def point_distance(x1,y1,x2,y2):
    return math.sqrt((x1 - x2)**2 + (y1-y2)**2)

#magic do not touch!!!! The success of this formula will determine the success of Spyglass
def calculate_score(factor, distance, tripexpert_score):
    #reverse the scaled distance scores so that small distances have a higher scaled score.
    scaled_distance = (factor['max_distance'] - (distance - factor['min_distance'])) / (factor['max_distance']-factor['min_distance'])
    scaled_tripexpert_score = (tripexpert_score - factor['min_score']) / (factor['max_score'] - factor['min_score'])
    return scaled_distance + scaled_tripexpert_score*100

def create_route():
    #####starting options######
    end_lat = 40.7484
    end_long = -73.9857
    curr_lat = end_lat
    curr_long = end_long
    remaining_distance = 10
    num_events = 5
    ###########################
    itinerary = []
    for i in range(num_events):
        venues = tripexpert_api_helper('venues?venue_type_id=3&destination_id=6&order_by=distance&latitude='+str(curr_lat)+'&longitude='+str(curr_long))
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
            venue_long = float(venue['latitude'])
            venue_lat = float(venue['longitude'])
            venue_score = venue['tripexpert_score']**2


            #calculate ellipse search area info:
            major_axis = remaining_distance
            '''
            foci_distance = point_distance(curr_long, end_long, curr_lat, end_lat)
            minor_axis = math.sqrt(major_axis**2 - foci_distance**2)
            center_long = math.abs((end_lat - curr_lat)/2)
            center_lat = math.abs((end_long-curr_long)/2)
            '''
            #end search if events are beyond search radius
            if distance > major_axis/2:
                break
            #skip if event is out of ellipse
            if distance + vincenty((curr_lat, curr_long), (end_lat, end_long)).miles > remaining_distance:
                continue
            #add venue to list of valid venues
            valid_venues.append(venue)
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
        venue_id_picker = []
        cum_score = 0
        for index, venue in enumerate(valid_venues):
            venue_score = calculate_score(factors, venue['distance'], venue['tripexpert_score'])
            cum_score += venue_score
            venue_score_picker.append(cum_score)
            venue_id_picker.append(index)
        #generate random number and binary search to find event.
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
