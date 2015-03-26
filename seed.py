"""Quick and dirty script to seed the DB. I have a text copy 
of valid data that was pulled from PostgreSQL on a previous app iteration."""

import os
import data_point_store
import model
from datetime import datetime


def main():

	dbsession = model.connect()

	hr_json = open('./raw_data/psql_output.txt').read()
	lines = hr_json.split('\n')
	
	for each_line in lines:
		# separate on pipes
		db_record_as_list = each_line.split('|')

		point = model.HRDataPoint()

		point.user_id = db_record_as_list[1].strip()
		point.bpm = db_record_as_list[2].strip()
		point.start_time = db_record_as_list[3].strip()
		point.end_time = db_record_as_list[4].strip()
		point.start_datetime = datetime.strptime(db_record_as_list[5].strip(), "%Y-%m-%d %H:%M:%S")
		point.end_datetime = datetime.strptime(db_record_as_list[6].strip(), "%Y-%m-%d %H:%M:%S")
		point.day_of_point = db_record_as_list[7].strip()

		# convert the t or f to an actual bool
		if db_record_as_list[8].strip() == 't':
			stressful = True
		elif db_record_as_list[8].strip() == 'f':
			stressful = False
		else:
			stressful = None

		point.is_stressful = stressful

		print "Here's the current data point: ", point
		dbsession.add(point)

	dbsession.commit()


if __name__ == '__main__': 
	main()