import pandas as pd
from dataclasses import dataclass

#class structure to hold information for each block
@dataclass
class block:
    name: int                #ex: 010010201001
    population: int          #ex: 457
    latitude: float          #ex: 32.4658291
    longitude: float         #ex: -86.4896143

#List of each of the columns in the csv file
col_list = ["census_block_group", "amount_land", "amount_water", "latitude", "longitude"]
#read each line in the csv file
#each column of the col_list will be filled with corresponding data
df = pd.read_csv("cbg_geographic_data.csv", usecols=col_list)

#print the latitude and longitude for every census block group
for i in range(len(df)):
    print(((df["census_block_group"]).iloc[i]), ((df["latitude"]).iloc[i]), ((df["longitude"]).iloc[i]))
