"""TODO import a time/calendar library to make it easier to filter the data points based on working hours."""

import Fit_OAuth as foa
from model import connect, HRDataPoint
from sqlalchemy.sql import and_
from datetime import timedelta
import nanotime
import numpy
import data_point_store
import json

DAY_IN_NANOSECS = 86400000000000
FIFTEEN_MINS_NANO = 900000000000

def check_for_new_bpm():
	"""This queries the DB for a user to see when the last bpm data refresh 
	was for that user, and if the last pull was > 24 hours ago, it calls
	fetch_data to add recent bpm data for that user. The user is currently
	hardcoded to me."""

	dbsession = connect()
	latest_datapoint = dbsession.query(HRDataPoint).filter_by(user_id=1).order_by(HRDataPoint.start_time.desc()).first()

	latest_timestamp = int(latest_datapoint.end_time)

	if latest_timestamp < (int(nanotime.now()) - DAY_IN_NANOSECS):
		endbound = str(int(nanotime.now())) # Get now in nanotime for the endbound of the dataset
		new_data = foa.fetch_data(data_type='bpm', startbound=latest_datapoint.end_time, endbound=endbound)
		data_point_store.save_to_db(new_data)
		return True
	else:
		print """No new data in the DB!
		check back in 24 hours."""
		return False


def is_motion_related(timestamp):
	"""This should take a single string that represents
	 a timestamp (in nanoseconds) for a datapoint that the calling function
	 needs to get related motion data for. It fetches all motion data in the Fit API 
	 from the 15 minutes preceeding the given timestamp. 

	 It returns true or false."""

	starttime = str(int(timestamp) - FIFTEEN_MINS_NANO)
	data_as_list = foa.fetch_data(startbound=starttime, endbound=timestamp, data_type='speed')

	d = json.loads(data_as_list)

	if 'point' not in d:
		print "key 'point' not in the dict returned from fitness.location.read"
		print "This is the thing we got back from Google: ", d
		return False

	return True


def is_stressful(data_point_time, bpm):
	"""This takes a datetime object as its parameter and determines if 
	data associated with it indicates stress by comparing to filtered datapoints from the preceeding week.
	The caller should expect a Boolean to be returned."""

	# Determine the startbound for the query:
	d = timedelta(days=-7)
	sb = data_point_time + d

	dbsession = connect()

	dataset = dbsession.query(HRDataPoint).filter(and_(HRDataPoint.start_datetime > sb, HRDataPoint.start_datetime < data_point_time)).all()

	bpm_list = []
	for each in dataset:
		bpm_list.append(each.bpm)

	print "this is the value of bpm_list: ", bpm_list

	mean_of_dataset = numpy.mean(bpm_list)

	print "the mean of the dataset is ", mean_of_dataset

	if bpm > (mean_of_dataset + 9):
		print True
		return True

	print False
	return False


def filter_bpm():
	"""This takes a list of HRDataPoint objects and filters out points
	which aren't in the ambient heart rate zone. It does this by checking
	for motion data shortly before data points which are 10 bpm or higher than the mean.

	Right now this is hardcoded to check *all* points in the HRDataPoint
	table, but would in the future need to take the user id as a parameter."""


	dbsession = connect()
	data_points = dbsession.query(HRDataPoint).filter_by(user_id=1).all()

	# Extract the bpm values so I can do math with them more easily:
	list_of_bpm = []

	for each_point in data_points:
		list_of_bpm.append(each_point.bpm)

	# Get the mean, and check which points are > 10 bpm of mean.
	mean_of_dataset = numpy.mean(list_of_bpm)
	# Create a counter for indexing purposes when deleting a data point
	counter = 0

	print "This is how many data points there are BEFORE: ", len(data_points)

	for each in data_points:
	# TEST THIS need to test with all the GF data; the test DB as it's 
	# seeded now doesn't have any data points that are motion related. 
		if each.bpm > (mean_of_dataset + 10):
			if is_motion_related(each.start_time) is True:
				data_points.remove(data_points[counter])

			counter += 1 

	print "This is how many data points there are AFTER: ", len(data_points)
	# Ultimately I'll return this to a view which will render it prettily for the user. 
	return data_points 


def fetch_weeks_data():
	"""Takes as parameter a week number (so 1 through 52) and returns a list of data 
	point objects that ocurred in that week."""
	# TODO make this dynamic, hardcoded to week 9 at the moment. 
	
	data_points = dbsession.query(HRDataPoint).filter(user_id=1).all()

	pass


def format_data_week(list_of_points):
	"""Takes a list of data point objects as parameter, returns a dictionary formatted
	like this: week = {'3-2': False, '3-3': False, '3-4': True}"""
	
	week_info = {}

	for each in list_of_points:
		k = each.day_of_point
		
		# If the day has already been flagged as True, keep iterating
		if week_info[k] == True:
			continue
		# If not, check if the day is stressful and add to dict:
		elif each.is_stressful == True:
			week_info[k] = True
		# Defaults to False if no other checks pass
		else:
			week_info[k] = False

	week = {
	'2015-02-03': True,
	'2015-03-03': False,
	'2015-04-03': False,
	'2015-05-03': True,
	'2015-06-03': False	
}

	return week


def format_data_day():
	"""Takes a single date as parameter and returns a list of data points for that day.

	This will take a string parameter formatted like this: '2015-24-02' """

	day = {
	'9 am': False,
	'10 am': False,
	'11 am': False,
	'noon': False,
	'1 pm': False,
	'2 pm': False,
	'3 pm': False,
	'4 pm': True,
	'5 pm': False
	}

	return day











