import glob
import json
import pickle
import sys
from collections import OrderedDict
from os import path, makedirs

import pandas as pd
from shapely.geometry import Polygon, MultiPolygon, Point
from tqdm import tqdm

from geographyHelper import shapelyGeometryToGeoJSON


def saveDataToDirectoryWithDescription(data, censusYear, stateName, descriptionOfInfo):
    directoryPath = path.expanduser('~/Documents/{0}-{1}-{2}Info'.format(censusYear, stateName, descriptionOfInfo))
    if not path.exists(directoryPath):
        makedirs(directoryPath)
    count = 1
    for dataChunk in data:
        filePath = '{0}/{1:09}.redistdata'.format(directoryPath, count)
        saveDataToFile(data=dataChunk, filePath=filePath)
        count += 1


def save_data_to_file_with_description(data, census_year, state_name, description_of_info):
    directory_path = path.expanduser('../results/algoData')
    if not path.exists(directory_path):
        makedirs(directory_path)
    file_path = path.expanduser(
        '../results/algoData/{0}-{1}-{2}Info.redistdata'.format(census_year, state_name, description_of_info))
    saveDataToFile(data=data, filePath=file_path)


def saveDataToFile(data, filePath):
    tqdm.write('*** Attempting to save: {0} ***'.format(filePath))
    sys.setrecursionlimit(100000)
    with open(filePath, 'w+b') as file:
        pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)
    tqdm.write('*** Saved: {0} ***'.format(filePath))


def saveGeoJSONToDirectoryWithDescription(geographyList, censusYear, stateName, descriptionOfInfo):
    directoryPath = path.expanduser('~/Documents/{0}-{1}-{2}Info'.format(censusYear, stateName, descriptionOfInfo))
    if not path.exists(directoryPath):
        makedirs(directoryPath)
    geoJSONObjects = []
    for geography in geographyList:
        if type(geography.geometry) is MultiPolygon:
            exteriors = [Polygon(polygon.exterior) for polygon in geography.geometry]
            exteriorPolygon = MultiPolygon(exteriors)
        else:
            exteriorPolygon = Polygon(geography.geometry.exterior)
        exteriorJSON = shapelyGeometryToGeoJSON(exteriorPolygon)
        geoJSONObjects.append(exteriorJSON)
    count = 1
    for jsonString in geoJSONObjects:
        filePath = '{0}/{1:04}.geojson'.format(directoryPath, count)
        tqdm.write('*** Attempting to save: {0} ***'.format(filePath))
        jsonObject = json.loads(jsonString)
        numberProperty = {'number': '{0}'.format(count)}
        jsonObject['properties'] = numberProperty
        jsonObject = OrderedDict([('type', jsonObject['type']),
                                  ('properties', jsonObject['properties']),
                                  ('coordinates', jsonObject['coordinates'])])
        jsonString = json.dumps(jsonObject)
        with open(filePath, "w") as jsonFile:
            print(jsonString, file=jsonFile)
        tqdm.write('*** Saved: {0} ***'.format(filePath))
        count += 1


def save_geojson_to_results(geography_list, state_name):
    # get number of voting booths for each district
    voting_booths = get_num_voting_booths(geography_list)

    geojson_objects = []
    district_populations = []
    for geography in geography_list:

        if type(geography.geometry) is MultiPolygon:
            exteriors = [Polygon(polygon.exterior) for polygon in geography.geometry]
            exterior_polygon = MultiPolygon(exteriors)
        else:
            exterior_polygon = Polygon(geography.geometry.exterior)

        exterior_json = shapelyGeometryToGeoJSON(exterior_polygon)
        district_pop = geography.population

        geojson_objects.append(exterior_json)
        district_populations.append(district_pop)

    with open('../results/{0}_Results.json'.format(state_name.abbr), 'w+') as json_file:
        # Load current results
        results_so_far = []

        district_num = 0
        for json_string in geojson_objects:
            new_district = {
                'type': 'Feature',
                'id': '{0}{1:0=2d}'.format(state_name.fips, district_num + 1),
                'properties': {
                    'name': '{0} {1:0=2d}'.format(state_name, district_num + 1),
                    'population': district_populations[district_num],
                    'num_voting_booths': voting_booths[district_num]
                },
                'geometry': json.loads(json_string)
            }

            results_so_far.append(new_district)
            district_num += 1

        # Overwrite file contents
        json_file.seek(0)
        json.dump(results_so_far, json_file)
        json_file.truncate()


def get_num_voting_booths(geography_list):
    voting_booths = []
    count = 0

    # create polygon
    for geography in geography_list:
        if type(geography.geometry) is MultiPolygon:
            exteriors = [Polygon(polygon.exterior) for polygon in geography.geometry]
            exterior_polygon = MultiPolygon(exteriors)
        else:
            exterior_polygon = Polygon(geography.geometry.exterior)

        # List of each of the columns in the public school csv file
        school_col_list = ["X", "Y", "OBJECTID", "NCESSCH", "NAME", "OPSTFIPS", "LSTREE", "LCITY", "LSTATE", "LZIP",
                           "LZIP4",
                           "STFIP15", "CNTY15", "NMCNTY15", "LOCALE15", "LAT1516", "LON1516", "CBSA15", "NMCBSA15",
                           "CBSATYPE15", "CSA15", "NMCSA15", "NECTA15", "NMNECTA15", "CD15", "SLDL15", "SLDU15"]
        # read each line in the csv file
        # each column of the col_list will be filled with corresponding data
        school_file = pd.read_csv("../Polling Locations CSV files/Public_School_Locations_201516.csv",
                                  usecols=school_col_list)

        # List of each of the columns in the public library csv file
        lib_col_list = ["Location Number", "Location Name", "Location Type", "Address", "City", "State", "Zip Code",
                        "Phone Number",
                        "County", "Latitude", "Longitude", "Accuracy"]
        # read each line in the csv file
        # each column of the col_list will be filled with corresponding data
        lib_file = pd.read_csv("../Polling Locations CSV files/public_libraries.csv",
                               usecols=lib_col_list)

        # initialize list
        voting_booths.append(0)

        # Create shapely point based on public school coordinates and check to see if point is contained in polygon
        # increment the number of voting booths by the number of points that lie in the polygon
        for i in range(len(school_file)):
            point = Point(((school_file["X"]).iloc[i]), ((school_file["Y"]).iloc[i]))

            if exterior_polygon.contains(point):
                voting_booths[count] = voting_booths[count] + 1

        for i in range(len(lib_file)):
            point = Point(((lib_file["Longitude"]).iloc[i]), ((lib_file["Latitude"]).iloc[i]))

            if exterior_polygon.contains(point):
                voting_booths[count] = voting_booths[count] + 1

        count = count + 1

    return voting_booths


def loadDataFromDirectoryWithDescription(censusYear, stateName, descriptionOfInfo):
    directoryPath = path.expanduser('~/Documents/{0}-{1}-{2}Info'.format(censusYear, stateName, descriptionOfInfo))
    data = []
    redistFilesInDirectory = glob.glob('{0}/*.redistdata'.format(directoryPath))
    redistFilesInDirectory.sort()
    for fileName in redistFilesInDirectory:
        data.append(loadDataFromFile(fileName))
    return data


def load_data_from_file_with_description(census_year, state_name, description_of_info):
    filePath = path.expanduser(
        '../results/algoData/{0}-{1}-{2}Info.redistdata'.format(census_year, state_name, description_of_info))
    return loadDataFromFile(filePath)


def loadDataFromFile(filePath):
    tqdm.write('*** Attempting to load: {0} ***'.format(filePath))
    with open(filePath, 'rb') as file:
        data = pickle.load(file)
        tqdm.write('*** Loaded: {0} ***'.format(filePath))
    return data
