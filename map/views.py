from django.http import HttpResponse
from django.shortcuts import render

import json

# rest framework
from rest_framework.views import APIView
from rest_framework.response import Response

from django.contrib.staticfiles.storage import staticfiles_storage

# Homepage view
def home_view(request, *args, **kwargs):
	return render(request, "home.html")

# Map view of the districts
def map_view(request, state, *args, **kwargs):
    url = 'static/state_locations/state-locations.json'
    f = open(url) 
    data = json.load(f) 

    lat = data[state]["Lat"]
    lon = data[state]["Lon"]

    return render(request, "map_view.html", {'state': state, 'lat': lat, 'lon': lon})


# Rest API to host JSON data for each state
class RestDashboardDistrictData(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self, request, state, format=None):      
        json_response = []
        filename = f'static/results/{state}_Results.json'
        with open(filename, 'r') as f:
            json_response = json.load(f)
        
        return Response(json_response)