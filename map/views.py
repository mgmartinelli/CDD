from django.http import HttpResponse
from django.shortcuts import render

import json

# rest framework
from rest_framework.views import APIView
from rest_framework.response import Response

def home_view(request, *args, **kwargs):
	return render(request, "home.html")

def map_view(request, state, *args, **kwargs):
	f = open('static/state_locations/state-locations.json') 
	data = json.load(f) 

	lat = data[state]["Lat"]
	lon = data[state]["Lon"]

	# all views will be linked to an actual HTML file when the project gets bigger
	return render(request, "map_view.html", {'state': state, 'lat': lat, 'lon': lon})

class RestDashboardDistrictData(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self, request, state, format=None):
        
        # Opening data from JSON file for development speed
        json_response = []
        filename = f'static/results/{state}_Results.json'
        with open(filename, 'r') as f:
            json_response = json.load(f)
        
        return Response(json_response)