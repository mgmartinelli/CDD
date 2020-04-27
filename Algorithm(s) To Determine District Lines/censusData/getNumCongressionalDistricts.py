from census import Census


def main(api_key, state_info):
    census_request = Census(api_key)

    congressional_district_data = census_request.acs1.state_congressional_district('NAME', state_info.fips, Census.ALL)

    return len(congressional_district_data)
