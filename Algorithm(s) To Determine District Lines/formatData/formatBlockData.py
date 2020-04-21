from exportData.exportData import save_data_to_file_with_description as save_data
from exportData.exportData import load_data_from_file_with_description as load_data
from formatData.redistrictingGroup import create_redistricting_groups_with_atomic_blocks_from_census_data, \
    prepare_graphs_for_redistricting_groups, prepare_block_graphs_for_redistricting_groups


def main(state_info, census_year=2010, description_to_work_with='All'):
    census_data = load_data(census_year, state_info.name, '{0}Block'.format(description_to_work_with))

    redistricting_group_list = create_redistricting_groups_with_atomic_blocks_from_census_data(census_data)

    save_data(redistricting_group_list, census_year, state_info.name,
              '{0}RedistrictingGroupPreGraph'.format(description_to_work_with))

    redistricting_group_list = prepare_block_graphs_for_redistricting_groups(redistricting_group_list)

    save_data(redistricting_group_list, census_year, state_info.name,
              '{0}RedistrictingGroupBlockGraphsPrepared'.format(description_to_work_with))

    redistricting_group_list = prepare_graphs_for_redistricting_groups(redistricting_group_list)
    save_data(redistricting_group_list, census_year, state_info.name,
              '{0}RedistrictingGroup'.format(description_to_work_with))
