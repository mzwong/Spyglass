from django.forms import ModelForm, Form, ChoiceField
from geoposition.forms import GeopositionField
from .models import *
from django import forms

class OptionsForm(ModelForm):
	OPTIONS = (("33", "Museums"),("34", "Outdoors"),("35", "Historical"))
	attraction_types = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=OPTIONS)
	class Meta:
		model = Itinerary
		fields = ['name', 'cost']

	starting_position = GeopositionField()
	ending_position = GeopositionField()
