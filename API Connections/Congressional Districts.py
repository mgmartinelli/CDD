from census import Census
from us import states

c = Census("78ae8c422513eb7551e52f2adf65ee6b51847b9d")

e = c.sf1.state_congressional_district('NAME', states.MD.fips, Census.ALL)
print("# of Congressional Districts in MD:", len(e))

f = c.sf1.state_congressional_district('NAME', states.CA.fips, Census.ALL)
print("# of Congressional Districts in CA:", len(f))