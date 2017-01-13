import os
def google_maps_key(request):
    return {'google_maps_key': os.environ.get('GEOPOSITION_GOOGLE_MAPS_API_KEY')}
