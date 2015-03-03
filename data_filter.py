"""TODO import a time library to make it easier to filter the data points based on working hours."""

import Fit_OAuth as foa
import model
import nanotime
import numpy
import data_point_store

DAY_IN_NANOSECS = 86400000000000
FIFTEEN_MINS_NANO = 900000000000

def check_for_new_bpm():
	"""This queries the DB for a user to see when the last bpm data refresh 
	was for that user, and if the last pull was > 24 hours ago, it calls
	fetch_data to add recent bpm data for that user. The user is currently
	hardcoded to me."""

	dbsession = model.connect()
	latest_datapoint = dbsession.query(model.HRDataPoint).filter_by(user_id=1).order_by(model.HRDataPoint.start_time.desc()).first()

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

	starttime = timestamp - FIFTEEN_MINS_NANO
	data_as_list = foa.fetch_data(startbound=starttime, endbound=timestamp, data_type='speed')

	print data_as_list

	




def filter_bpm():
	"""This takes a list of HRDataPoint objects and filters out points
	which aren't in the ambient heart rate zone. It does this by checking
	for motion data shortly before data points which are 10 bpm or higher than the mean.

	Right now this is hardcoded to check *all* points in the HRDataPoint
	table, but would in the future need to take the user id as a parameter."""

	dbsession = model.connect()
	all_data_points = dbsession.query(model.HRDataPoint).filter_by(user_id=1).all()

	# Extract the bpm values so I can do math with them more easily:
	list_of_bpm = []

	for each_point in all_data_points:
		list_of_bpm.append(each_point.bpm)

	# Get the mean, and check which points are > 10 bpm of mean.
	mean_of_dataset = numpy.mean(list_of_bpm)

	for each in all_data_points:
		if each.bpm > (mean_of_dataset + 10):
			# Call is_motion_related, passing it the starttime 
			# attribute of the data point. If check returns true,
			# remove it from the list of points. 
			print "I am 10 or more higher than the mean."

	return list_of_bpm



filter_bpm()









