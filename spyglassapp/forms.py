from django.forms import ModelForm, Form, ChoiceField
from geoposition.forms import GeopositionField
from .models import *
from django import forms

class OptionsForm(ModelForm):
	class Meta:
		model = Itinerary
		fields = ['name', 'cost']

	starting_position = GeopositionField()
	ending_position = GeopositionField()
