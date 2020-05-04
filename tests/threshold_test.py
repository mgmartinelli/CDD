import json
import glob

""" 
threshold_test
Input: path_to_file (string) - path to the json file containing population and num_voting_booths of each state
	   metric (string) - "population" or "num_voting_booths"
	   error_percentage (float) - error percentage or threshold
	   verbose (boolean) - if set to True, displays which districts passed and which ones fail, 
	   					   else just displays how many districts passed the test
"""
def threshold_test(path_to_file, metric, error_percentage, verbose):

	if metric != "population" and metric != "num_voting_booths":
		print("Error: Wrong metric")
		return

	# Parsing JSON file as dictionary
	f = open(path_to_file) 
	data = json.load(f) 

	# Calculate total population/voting booths and number of districts
	sum = 0;
	num_dist = 0;
	for i in data:
		val = i["properties"][metric]
		num_dist += 1
		sum += val

	# Calculate average population/voting booths per district
	avg = sum / num_dist

	# calculate upper and lower bound
	upper = avg * (1 + error_percentage)
	lower = avg * (1 - error_percentage)

	# get the number of states passed
	passed = 0
	name = None
	for i in data:
		val = i["properties"][metric]
		name = i["properties"]["name"]
		if val <= upper and val >= lower:
			if verbose:
				print(f"Passed district {name}")
			passed += 1
		else:
			if verbose:
				print(f"Failed district {name}")

	if(passed/num_dist == 1):
		print(f"{name[0:len(name)-3]} Results: All {num_dist} districts passed")
	else:
		print(f"{name[0:len(name)-3]} Results: {num_dist-passed}/{num_dist} failed")


if __name__ == "__main__":
	
	JSON_results = glob.glob("./../Algorithm(s) To Determine District Lines/results/*_Results.json")

	pop_thresh = 0.03
	print(f"***** Population Tests: (Threshold: {pop_thresh*100}%) ******")
	for result in JSON_results:
		threshold_test(result, "population", pop_thresh, False)

	voting_thresh = 0.46
	print()
	print(f"***** Voting Booths Tests: (Threshold: {voting_thresh*100}%) ******")
	for result in JSON_results:
		threshold_test(result, "num_voting_booths", voting_thresh, False)
