"""One time script to seed the DB. I manually pulled some data using Google's OAuth playground interface,
and am adding those data points with this script. This way my program has a timestamp in the DB it can use
to construct all subsequent API calls for HR data."""

import os
import json
import model
import nanotime
from datetime import datetime


def main():

	session = model.connect()

	hr_json = open('./raw_data/hr_manual.txt').read()

	data = json.loads(hr_json)
	datapoint = model.HRDataPoint()

	""" 'each' is a dictionary. 'each' will become a single DB record; this loop 
		parses the json and assigns its values to the datapoint object, then adds it to the SQL 
		session to commit at the end."""
	# FIXME The SQL statements that the console outputs for the code below
	# is what I would expect, but when I check the DB I only
	# see the most recent data point in the table. Investigate on Monday.

	for each in data['point']:
		print type(each)
		datapoint.user_id = 1 # Need to hardcode this to my user_id to satisfy FK constraint
		datapoint.bpm = each['value'][0]['fpVal'] #This is a float
		datapoint.start_time = each['startTimeNanos']
		datapoint.end_time = each['endTimeNanos']

		session.add(datapoint)

		session.commit()


if __name__ == '__main__': 
	main()