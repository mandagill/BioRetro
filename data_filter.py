"""TODO import a time library to make it easier to filter the data points based on working hours."""

import Fit_OAuth as foa
import model
import nanotime
import data_point_store

DAY_IN_NANOSECS = 86400000000000

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
		print "False"
		return False


def check_speed(timestamp):
	"""This should take a single string that represents
	 a timestamp (in nanoseconds) for a datapoint that the calling function
	 needs to get related motion data for. It fetches all motion data in the Fit API 
	 from the 15 minutes preceeding the given timestamp."""
	pass

