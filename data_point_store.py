import json
import model
import nanotime
import psycopg2


def save_to_db(data_as_string):
	""" 'each' is a dictionary. 'each' will become a single DB record; this loop 
		parses the json and assigns its values to the datapoint object, then adds it to the SQL 
		session to commit at the end."""

	data_dict = json.loads(data_as_string)
	session = model.connect()

	for each in data_dict['point']:
		
		datapoint = model.HRDataPoint()
		datapoint.user_id = 1 # Need to hardcode this to my user_id to satisfy FK constraint
		datapoint.bpm = each['value'][0]['fpVal'] #This is a float
		datapoint.start_time = each['startTimeNanos']
		datapoint.end_time = each['endTimeNanos']
		# TODO Edit to also insert day and is_stressful info per new schema

		session.add(datapoint)
	
	session.commit()


def create_day(dataset):
	"""This stores the state of stressful or not stressful to 
	the database for a given day. Arranging the days 
	in a week is done on the front end."""
	pass