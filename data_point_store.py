import json
import model
from datetime import datetime
import psycopg2


def save_to_db(data_as_string):
	""" 'each' is a dictionary. 'each' will become a single DB record; this loop 
		parses the json and assigns its values to the datapoint object, then adds it to the SQL 
		session to commit at the end."""
		 
		 # TODO need a way of checking the DB if there is a 
		 # day in there already and if not, to add the day w/ 
		 # is_stress being null. 

	data_dict = json.loads(data_as_string)
	dbsession = model.connect()

	for each in data_dict['point']:
		# Create a datapoint oject
		datapoint = model.HRDataPoint()
		# Assign its attributes according to the dictionary contents
		datapoint.user_id = 1 # Need to hardcode this to my user_id to satisfy FK constraint
		datapoint.bpm = each['value'][0]['fpVal']
		datapoint.start_time = each['startTimeNanos']
		datapoint.end_time = each['endTimeNanos']
		datapoint.start_datetime = convert_to_datetime(datapoint.start_time)
		datapoint.end_datetime = convert_to_datetime(datapoint.end_time)
		# Converting type over two lines for readability 
		dt = convert_to_datetime(datapoint.start_time)
		datapoint.day_of_point = dt.strftime('%Y-%m-%d')

		datapoint.is_stressful = is_stressful()

		# Add the datapoint to the db session
		dbsession.add(datapoint)
	
	dbsession.commit()


def convert_to_datetime(nanotime_as_string):
	"""Using the datetime library, this converts the given nanotime stamp and 
	returns the datetime of that time stamp as a string."""

	ts_int = int(nanotime_as_string)
	ts = datetime.fromtimestamp(ts_int/1000000000)

	return ts









