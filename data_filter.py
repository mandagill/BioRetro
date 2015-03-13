import Fit_OAuth as foa
from model import connect, HRDataPoint
from sqlalchemy.sql import and_, asc
from datetime import timedelta, time, datetime
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
	
	latest_datapoint = result.first()
	latest_timestamp = int(latest_datapoint.end_time)
	now_in_nanotime = nanotime.now()

	if latest_timestamp < (int(nanotime.now()) - DAY_IN_NANOSECS):
		endbound = str(int(nanotime.now())) # Get now in nanotime for the endbound of the dataset
		new_data = foa.fetch_data(data_type='bpm', startbound=latest_datapoint.end_time, endbound=endbound)
		data_point_store.save_to_db(new_data)
		return True
	else:
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
	# "point" is the name of the list that the Fit API returns. The JSON object gives us header info in the dict,
	# and that dict contains a list of data points. If there's nothing in that list, there's no data.
	if 'point' not in d:
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

	mean_of_dataset = numpy.mean(bpm_list)

	if bpm > (mean_of_dataset + 9):
		return True

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

	one_weeks_data = dbsession.query(HRDataPoint).filter(HRDataPoint.start_datetime>startbound, HRDataPoint.start_datetime<endbound ).all()

	return one_weeks_data


def format_data_week(list_of_points):
	"""Takes a list of data point objects as parameter, returns a dictionary formatted
	like this: week = {'3-2': False, '3-3': False, '3-4': True}"""

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

	return week_info


def generate_days_index(week_number):
	"""Function returns a list of dates for the requested week as strings. 
	Writing to resolve GitHub issue #5. The controller will call this so the view
	knows the correct order to display the is_stressful booleans."""

	week = Week(2015, week_number)

	days = [
		week.monday(),
		week.tuesday(),
		week.wednesday(),
		week.thursday(),
		week.friday()
	]

	days_index = []	

	for each in days:
		# stringify the date and add it to the list to return
		days_index.append(str(each))

	return days_index


def render_data(week_number):
	"""This is a wrapper function to prep the week data for the view. It will
	return a dictionary of values and a list to order the data with when the
	Jinja template is generated."""
	# Retrieve data for the given week and format it:
	list_of_data = fetch_weeks_data(int(week_number))
	one_weeks_data = format_data_week(list_of_data)

	# Go get an ordered list of dates for the given week for sorting the data:
	sort_keys = generate_days_index(int(week_number))

	return sort_keys, one_weeks_data



def format_data_day(day_string):
	"""Takes a single date as parameter and returns a dict of times during the 
	day as keys and boolean values.
	This will take a string parameter formatted like this: '2015-24-02' """

	dbsession = connect()
	result = dbsession.query(HRDataPoint).filter_by(day_of_point=day_string).all()
	# Need to unpack the data queried from the DB before checking for stress
	day_data = []

	for each_record in result:
		day_data.append(each_record)

	# Need to extract the time from the datetime attribute, 
	# so make a dict of {<time> : <boolean>} pairs:
	dict_day_booleans = {}

	for each_point in day_data:

		dt = each_point.start_datetime
		hour_of_point = dt.hour

		dict_day_booleans[hour_of_point] = each_point.is_stressful

	# Reference the dict indexed by time and create a timestring/bool dict to return:
	to_display = {}
	dict_keys = dict_day_booleans.keys()

	for a_key in dict_keys:
		if a_key < 10:
			to_display['9 am'] = dict_day_booleans.get(a_key)
		elif a_key < 11:
			to_display['10 am'] = dict_day_booleans.get(a_key)
		elif a_key < 12:
			to_display['11 am'] = dict_day_booleans.get(a_key)
		elif a_key < 13:
			to_display['noon'] = dict_day_booleans.get(a_key)
		elif a_key < 14:
			to_display['1 pm'] = dict_day_booleans.get(a_key)
		elif a_key < 15:
			to_display['2 pm'] = dict_day_booleans.get(a_key)
		elif a_key < 16:
			to_display['3 pm'] = dict_day_booleans.get(a_key)
		elif a_key < 17:
			to_display['4 pm'] = dict_day_booleans.get(a_key)
		elif a_key < 18:
			to_display['5 pm'] = dict_day_booleans.get(a_key)
		elif a_key < 19:
			to_display['6 pm'] = dict_day_booleans.get(a_key)
		else:
			pass

	return to_display







