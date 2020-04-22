from us import states
from censusData.getBlockData import main as get_block_data
from censusData.getNumCongressionalDistricts import main as get_num_congressional_districts
from formatData.formatBlockData import main as format_block_data
from redistrict.createDistricts import main as create_districts
from exportData.exportData import save_geojson_to_results as save_geojson


def main():
    api_key = "78ae8c422513eb7551e52f2adf65ee6b51847b9d"
    state_abbreviation = 'DE'
    state_info = states.lookup(state_abbreviation)

    # get_block_data(api_key, state_info)
    # format_block_data(state_info)

    num_congressional_districts = get_num_congressional_districts(api_key, state_info)
    districts = create_districts(state_info, num_congressional_districts, 0.03)
    save_geojson(districts, state_info)


main()
