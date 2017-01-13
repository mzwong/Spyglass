from django.forms import ModelForm, Form
from geoposition.forms import GeopositionField
from .models import *

class OptionsForm(ModelForm):
	class Meta:
		model = Itinerary
		fields = ['name']

	starting_position = GeopositionField()
	ending_position = GeopositionField()