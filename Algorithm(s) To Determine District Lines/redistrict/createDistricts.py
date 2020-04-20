from exportData.exportData import load_data_from_file_with_description, save_data_to_file_with_description
from geographyHelper import population_deviation_from_percent
from redistrict.district import create_district_from_redistricting_groups, WeightingMethod, BreakingMethod


def main(state_info, number_of_districts, margin_of_error, census_year=2010, description_to_work_with='All'):
    redistricting_groups = load_data_from_file_with_description(census_year=census_year,
                                                                state_name=state_info.name,
                                                                description_of_info='{0}RedistrictingGroup'.format(
                                                                    description_to_work_with))

    initial_district = create_district_from_redistricting_groups(redistricting_groups=redistricting_groups)

    population_deviation = population_deviation_from_percent(margin_of_error, number_of_districts,
                                                             initial_district.population)

    districts = initial_district.split_district(number_of_districts=number_of_districts,
                                                population_deviation=population_deviation,
                                                weighting_method=WeightingMethod.cardinalDistance,
                                                breaking_method=BreakingMethod.splitGroupsOnEdge,
                                                should_merge_into_former_redistricting_groups=True,
                                                should_draw_each_step=False,
                                                should_refill_each_pass=True,
                                                fast_calculations=False,
                                                show_detailed_progress=False)

    save_data_to_file_with_description(data=districts,
                                       census_year=census_year,
                                       state_name=state_info,
                                       description_of_info='{0}-FederalDistricts'.format(description_to_work_with))

    return districts
