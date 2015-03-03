"""One time script to seed the DB. I manually pulled some data using Google's OAuth playground interface,
and am adding those data points with this script. This way my program has a timestamp in the DB it can use
to construct all subsequent API calls for HR data."""

import os
import data_point_store


def main():
	hr_json = open('FILL_IN').read()
	data_point_store.save_to_db(hr_json)


if __name__ == '__main__': 
	main()