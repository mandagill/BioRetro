import json
import model
from datetime import datetime, time
import psycopg2
import data_filter


WORK_START = time(9, 0, 0)
WORK_END = time(18, 30, 0)


def save_to_db(data_as_string):
	""" 'each' is a dictionary. 'each' will become a single DB record; this loop 
		parses the json and assigns its values to the datapoint object, then adds it to the SQL 
		session to commit at the end.""" 

	data_dict = json.loads(data_as_string)
	dbsession = model.connect()

	for each in data_dict['point']:
		# Create a datapoint oject
		datapoint = model.HRDataPoint()

		# Assign its attributes according to the dictionary contents.
		datapoint.user_id = 1 # Need to hardcode this to me until multiple users/logins are supported. 
		datapoint.bpm = each['value'][0]['fpVal']
		datapoint.start_time = each['startTimeNanos']
		datapoint.end_time = each['endTimeNanos']
		datapoint.start_datetime = convert_to_datetime(datapoint.start_time)
		datapoint.end_datetime = convert_to_datetime(datapoint.end_time)

		sdt = convert_to_datetime(datapoint.start_time)
		time_of_sdt = sdt.time()

		# Make sure the point is in working hours before writing it to the DB:
		if not (time_of_sdt > WORK_START) & (time_of_sdt < WORK_END):
			continue #I expect this to go to the next point in data_dict in line 16

		datapoint.day_of_point = sdt.strftime('%Y-%m-%d')
		
		# Check if the datapoint is stressful when compared to existing DB data
		datapoint.is_stressful = data_filter.is_stressful(datapoint.start_datetime, datapoint.bpm)
		
		# Make sure elevated bpm isn't motion related before writing it to the DB
		if datapoint.is_stressful:
			if data_filter.is_motion_related(datapoint.start_time):
				print "the datapoint is stressful, using continue."
				continue

		# Add the datapoint to the db session
		dbsession.add(datapoint)
		# Putting the commit *inside* the loop so that the
		# is_stressful function can use the committed datapoints
		# when it calls the db. Not as performant but it
		# makes the calculations more accurate.
		dbsession.commit()


def convert_to_datetime(nanotime_as_string):
	"""Using the datetime library, this converts the given nanotime stamp and 
	returns the datetime of that time stamp as a string."""

	ts_int = int(nanotime_as_string)
	ts = datetime.fromtimestamp(ts_int/1000000000)

	return ts









