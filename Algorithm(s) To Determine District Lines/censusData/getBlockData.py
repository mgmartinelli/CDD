import math
import time

from census import Census
from esridump.dumper import EsriDumper
from us import states

from exportData.exportData import save_data_to_file_with_description as save_data


def get_counties_in_state(census_request, state_fips_code, max_number_of_counties=math.inf,
                          specific_counties_only=None):
    requested_counties = census_request.sf1.get(fields='NAME',
                                                geo={'for': 'county:*', 'in': 'state:{0}'.format(state_fips_code)})

    requested_state = states.lookup(state_fips_code)
    state_name = requested_state.name
    for requested_county in requested_counties:
        county_name = requested_county['NAME'].replace(', {0}'.format(state_name), '')
        requested_county['NAME'] = county_name

    if specific_counties_only is not None:
        list_of_specific_counties = []
        for specific_county in specific_counties_only:
            matching_county = next((item for item in requested_counties if
                                    item['NAME'] == '{0} County'.format(specific_county)), None)
            list_of_specific_counties.append(matching_county)
        requested_counties = list_of_specific_counties

    if max_number_of_counties == math.inf:
        max_number_of_counties = len(requested_counties)
        requested_counties = requested_counties[:max_number_of_counties]

    return requested_counties


def get_blocks_in_county(state_fips_code, county_fips_code, census_request):
    # DEPRECATED: P0010001 is the total population as defined by: https://api.census.gov/data/2010/sf1/variables.html
    # The API now defaults to: https://api.census.gov/data/2010/dec/sf1/variables.html
    # Which now uses: P001001 for total population
    county_blocks = census_request.sf1.get(fields='P001001',
                                           geo={'for': 'block:*', 'in': 'state:{0} county:{1}'.format(
                                               state_fips_code, county_fips_code)})
    return county_blocks


def get_all_blocks_in_state(census_request, county_list, max_number_of_counties=math.inf):
    full_block_list = []

    # getting population counts and Block names for each county
    print('*** Getting all blocks and population counts in state ***')
    count = 0
    for county in county_list:
        if count >= max_number_of_counties:
            break
        county_fips = county['county']
        blocks_in_county = get_blocks_in_county(county['state'], county_fips, census_request)
        full_block_list += blocks_in_county
        print('Got all blocks and population counts in {0}'.format(county['NAME']))
        count += 1

    return full_block_list


def all_geo_data_for_each_block(county_info_list, existing_block_data):
    if len(existing_block_data) > 0:
        print('*** Getting geo info on all blocks ***')
        state_fips_code = existing_block_data[0]['state']

        start_time_for_processing_state = time.localtime()
        full_block_list_with_geo = []
        for county in county_info_list:
            print('Getting all geo info in {0}'.format(county['NAME']))
            start_time_for_processing_county = time.localtime()
            county_fips_code = county['county']

            block_geometries = EsriDumper(
                url='https://tigerweb.geo.census.gov/arcgis/rest/services/Census2010/tigerWMS_Census2010/MapServer/14',
                extra_query_args={'where': 'STATE=\'{0}\' AND COUNTY=\'{1}\''.format(state_fips_code, county_fips_code),
                                  'orderByFields': 'TRACT, BLKGRP, BLOCK'},
                timeout=120)  # extending timeout because there were some long load times
            # https://github.com/openaddresses/pyesridump

            for block_geometry in block_geometries:
                block_geo_properties = block_geometry['properties']
                block_geo_state_fips = block_geo_properties['STATE']
                block_geo_county_fips = block_geo_properties['COUNTY']
                block_geo_tract_fips = block_geo_properties['TRACT']
                block_geo_block_fips = block_geo_properties['BLOCK']

                matching_block_data = next((item for item in existing_block_data if
                                            item['state'] == block_geo_state_fips and
                                            item['county'] == block_geo_county_fips and
                                            item['tract'] == block_geo_tract_fips and
                                            item['block'] == block_geo_block_fips), None)

                matching_block_data['geometry'] = block_geometry['geometry']
                full_block_list_with_geo.append(matching_block_data)

            end_time_for_processing_county = time.localtime()
            elapsed_seconds_for_processing_county = (
                    time.mktime(end_time_for_processing_county) - time.mktime(start_time_for_processing_county))
            print('   {0} took {1} seconds'.format(county['NAME'], elapsed_seconds_for_processing_county))

        end_time_for_processing_state = time.localtime()
        elapsed_minutes_for_processing_state = (time.mktime(end_time_for_processing_state) - time.mktime(
            start_time_for_processing_state)) / 60
        print('It took {0} total minutes to get all the requested block geo data'.format(
            elapsed_minutes_for_processing_state))
        return full_block_list_with_geo

    else:
        return None


def all_geo_data_for_each_county(existing_county_data):
    if len(existing_county_data) > 0:
        print('*** Getting geo info on all counties ***')
        state_fips_code = existing_county_data[0]['state']

        start_time_for_processing_state = time.localtime()
        full_county_list_with_geo = []

        where_argument = 'STATE=\'{0}\' AND ('.format(state_fips_code)

        for county in existing_county_data:
            where_argument = '{0}NAME=\'{1}\''.format(where_argument, county['NAME'])
            if existing_county_data.index(county) != len(existing_county_data) - 1:
                where_argument = '{0} OR '.format(where_argument)

        where_argument = '{0})'.format(where_argument)

        county_geometries = EsriDumper(
            url='https://tigerweb.geo.census.gov/arcgis/rest/services/Census2010/tigerWMS_Census2010/MapServer/90',
            extra_query_args={'where': where_argument,
                              'orderByFields': 'COUNTY'})
        # https://github.com/openaddresses/pyesridump

        for countyGeometry in county_geometries:
            county_geo_properties = countyGeometry['properties']
            county_geo_state_fips = county_geo_properties['STATE']
            county_geo_county_fips = county_geo_properties['COUNTY']

            matching_county_data = next((item for item in existing_county_data if
                                         item['state'] == county_geo_state_fips and
                                         item['county'] == county_geo_county_fips), None)

            matching_county_data['geometry'] = countyGeometry['geometry']
            full_county_list_with_geo.append(matching_county_data)

        end_time_for_processing_state = time.localtime()
        elapsed_minutes_for_processing_state = (
                time.mktime(end_time_for_processing_state) - time.mktime(start_time_for_processing_state))
        print('It took {0} total seconds to get all the requested county geo data'.format(
            elapsed_minutes_for_processing_state))
        return full_county_list_with_geo
    else:
        return None


def main(api_key, state_info, census_year=2010, description_to_work_with='All'):
    census_request = Census(api_key, year=census_year)
    county_info_list = get_counties_in_state(census_request, state_fips_code=state_info.fips)

    all_blocks_in_state = get_all_blocks_in_state(census_request=census_request, county_list=county_info_list)
    all_block_geos_in_state = all_geo_data_for_each_block(county_info_list=county_info_list,
                                                          existing_block_data=all_blocks_in_state)

    # Save block data to file
    save_data(data=all_block_geos_in_state, census_year=census_year, state_name=state_info.name
              , description_of_info='{0}Block'.format(description_to_work_with))
