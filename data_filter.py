import Fit_OAuth as foa
from model import connect, HRDataPoint
from sqlalchemy.sql import and_, asc
from datetime import timedelta
import nanotime
import numpy
import data_point_store
import json
from isoweek import Week

DAY_IN_NANOSECS = 86400000000000
FIFTEEN_MINS_NANO = 900000000000

def check_for_new_bpm():
	"""This queries the DB for a user to see when the last bpm data refresh 
	was for that user, and if the last pull was > 24 hours ago, it calls
	fetch_data to add recent bpm data for that user. The user is currently
	hardcoded to me."""

	dbsession = connect()
	result = dbsession.execute('select * from "HRDataPoints" order by start_datetime desc limit 1')
	# import pdb; pdb.set_trace()
	
	latest_datapoint = result.first()
	latest_timestamp = int(latest_datapoint.end_time)
	print "This is the start point for the API call: ", latest_datapoint.start_time, "which is ", latest_datapoint.start_datetime
	now_in_nanotime = nanotime.now()
	print "This is the endbound for the API call: ", now_in_nanotime

	if latest_timestamp < (int(nanotime.now()) - DAY_IN_NANOSECS):
		endbound = str(int(nanotime.now())) # Get now in nanotime for the endbound of the dataset
		new_data = foa.fetch_data(data_type='bpm', startbound=latest_datapoint.end_time, endbound=endbound)
		data_point_store.save_to_db(new_data)
		return True
	else:
		print """No new data in the DB!
		check back in 24 hours."""
		# TODO return the string to the ajax caller so the user will
		# see the message.
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


def fetch_weeks_data(week_number):
	"""Takes as parameter a week number (so 1 through 52) and returns a list of data 
	point objects that ocurred in that week. It currently assumes the year is 2015; this will
	need to be refactored in later iterations.""" 
	dbsession = connect()

	requested_week = Week(2015, week_number)
	# These functions return datetime objects. I <3 the isoweek library zomg.
	startbound = requested_week.monday()
	endbound = requested_week.saturday() #This doesn't *include* data from the endbound day, just up to that day.
	print endbound

	one_weeks_data = dbsession.query(HRDataPoint).filter(HRDataPoint.start_datetime>startbound, HRDataPoint.start_datetime<endbound ).all()

	# Need to unpack the data points contained in the query result object because SQLAlchemy is mildly annoying like that.
	datapoints = []

	for each in one_weeks_data:
		datapoints.append(each)

	return datapoints


def format_data_week(list_of_points):
	"""Takes a list of data point objects as parameter, returns a dictionary formatted
	like this: week = {'3-2': False, '3-3': False, '3-4': True}

	It also returns a list of keys sorted chronologically so the view can 
	present the data in a week calendar format."""
	# FIX ME FIX ME FIX MEEEEE Dictionaries aren't sorted so the view currently
	# shows the user data out of order. Tracked in issue #5
	week_info = {}

	for each in list_of_points:
		# Get the date as a string to use as key to the dictionary to return
		k = each.day_of_point

		# Checking if the key is in the dict first, and if not, add it:
		if k not in week_info:
			if each.is_stressful == True:
				week_info[k] = True
			else:
				week_info[k] = False
		# If it's in the dict, update the record.
		if each.is_stressful is True:
			week_info[k] = True
		# If the current point is False but there is already a True
		# point in the dict, check so as not to override.
		elif week_info.get(k) is True:
			continue
		else:
			week_info[k] = False

		print week_info

	# keys = week_info.getkeys()

	return week_info


def format_data_day(day_string):
	"""Takes a single date as parameter and returns a dict of times during the 
	day as keys and boolean values.
	This will take a string parameter formatted like this: '2015-24-02' """

	dbsession = connect()
	result = dbsession.query(HRDataPoint).filter_by(day_of_point=day_string).all()
	day_data = []
	# Need to unpack the data queried from the DB before checking for stress
	for each in result:

		# if each.start_datetime  
		print "current datapoint, is_stressful is: ", each.is_stressful
		day_data.append(each)

	# TODO build a dictionary with times as keys and Booleans for values.

	return day_data











