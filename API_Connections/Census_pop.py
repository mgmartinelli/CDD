#manipulate dataframes in python
import pandas as pd

#make API calls with python
import requests

#allows us to store results of API call cleanly
import json

state = '01'
county = '001'

APIquery = f"https://api.census.gov/data/2010/dec/pl?get=P001001,NAME&for=block%20group:*&in=state:{state}%20county:{county}&key=78ae8c422513eb7551e52f2adf65ee6b51847b9d"
#construct the API call we will use
#APIquery = "https://api.census.gov/data/2010/dec/pl?get=P003001,NAME&for=block%20group:*&in=state:01%20county:073&key=78ae8c422513eb7551e52f2adf65ee6b51847b9d"

response = requests.get(APIquery)
formatResponse = json.loads(response.text)[1:]





#store the response in a dataframe
data_results = pd.DataFrame(columns=['Population',' Name',' State',' County',' Tract',' Block_Group'], data=formatResponse)

#save that dataframe to a CSV spreadsheet
data_results.to_csv('test1_query.csv', index=False)