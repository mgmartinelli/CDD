import glob
import json
import pickle
import sys
from collections import OrderedDict
from os import path, makedirs

from shapely.geometry import Polygon, MultiPolygon
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


def saveDataToFileWithDescription(data, censusYear, stateName, descriptionOfInfo):
    filePath = path.expanduser(
        '~/Documents/{0}-{1}-{2}Info.redistdata'.format(censusYear, stateName, descriptionOfInfo))
    saveDataToFile(data=data, filePath=filePath)


def saveDataToFile(data, filePath):
    tqdm.write('*** Attempting to save: {0} ***'.format(filePath))
    sys.setrecursionlimit(100000)
    with open(filePath, 'wb') as file:
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

    with open('../results/us-states-population-emphasis.json', 'r+') as json_file:
        # Load current results
        results_so_far = json.load(json_file)
        num_results_so_far = len(results_so_far["features"])

        district_num = 0
        for json_string in geojson_objects:
            new_district = {
                'type': 'Feature',
                'id': '{0:0=2d}'.format(num_results_so_far + 1),
                'properties': {
                    'name': '{0} {1:0=2d}'.format(state_name, district_num + 1),
                    'population': district_populations[district_num]
                },
                'geometry': json.loads(json_string)
            }

            results_so_far["features"].append(new_district)
            num_results_so_far += 1
            district_num += 1

        # Overwrite file contents
        json_file.seek(0)
        json.dump(results_so_far, json_file)
        json_file.truncate()


def loadDataFromDirectoryWithDescription(censusYear, stateName, descriptionOfInfo):
    directoryPath = path.expanduser('~/Documents/{0}-{1}-{2}Info'.format(censusYear, stateName, descriptionOfInfo))
    data = []
    redistFilesInDirectory = glob.glob('{0}/*.redistdata'.format(directoryPath))
    redistFilesInDirectory.sort()
    for fileName in redistFilesInDirectory:
        data.append(loadDataFromFile(fileName))
    return data


def loadDataFromFileWithDescription(censusYear, stateName, descriptionOfInfo):
    filePath = path.expanduser(
        '~/Documents/{0}-{1}-{2}Info.redistdata'.format(censusYear, stateName, descriptionOfInfo))
    return loadDataFromFile(filePath)


def loadDataFromFile(filePath):
    tqdm.write('*** Attempting to load: {0} ***'.format(filePath))
    with open(filePath, 'rb') as file:
        data = pickle.load(file)
        tqdm.write('*** Loaded: {0} ***'.format(filePath))
    return data
