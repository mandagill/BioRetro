import os
import requests
import json

# r = requests.get('')

hr_json = open('hr_manual.txt').read()

data = json.loads(hr_json)

for dp_as_dict in data['point']:
	# Each is a dictionary, extract value and add it to the db
	print dp_as_dict