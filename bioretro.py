import Fit_OAuth as foa
from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for, render_template
from flask.json import jsonify
import json
import os
import data_filter as data_filter
from isoweek import Week


ORDERED_KEY_LIST_DAY = [
	'9 am',
	'10 am',
	'11 am',
	'noon',
	'1 pm',
	'2 pm',
	'3 pm',
	'4 pm',
	'5 pm',
	'6 pm'
	]

DATA_UPDATE_RESPONSES = {
	'success': "Your data has been updated!",
	'fail': "No new data recently! check back in 24 hours.",
	'other': "Something unexpected happened, check with the webmistress."
}


os.environ['DEBUG'] = '1'

app = Flask(__name__)
app.secret_key = "pleasedon'tmockmethisisfordevonlyNOTAREALKEY"


@app.route('/authorize_google')
def authorize_api():
	"""OAuth step 1: redirect the user to Google so that they can see and approve the API permissions."""
	
	auth_url = foa.go_to_google()
	return redirect(auth_url)


@app.route('/callback', methods=['GET', 'POST'])
def get_token():
	"""OAuth step 2: using the code returned from Google, request an authorization token 
	to access Google Fit BPM and motion data sets."""

	code = request.args.get('code')
	foa.callback(code)
	return render_template('okauth.html')


@app.route('/landing')
def go_to_landing():
	# Interstitial landing page fixes issue #2
	return render_template('landing.html')


@app.route('/fetch_data')
def fetch_data():

	result = data_filter.check_for_new_bpm()

	if result is False:
		print "No new data"
		return DATA_UPDATE_RESPONSES['fail']
	elif result is True:
		print "I got your data!"
		return DATA_UPDATE_RESPONSES['success']
	else:
		print "FAILWHALE."
		return DATA_UPDATE_RESPONSES['other']


@app.route('/check_week_number')
def get_week_number():
	"""Check what the current week is and return the correct week number to display 
	to the user. The function will just return a week number as a string to append to 
	the next route the user will be directed to."""
	# TODO refactor this to support multi-year data; program currently assumes the year is 2015.
	this_week = str(Week.thisweek())
	week_num_str = this_week[-2:]
	week_num_int = int(week_num_str)
	
	# need to decrement so we see the last *full week's* data
	week_num = week_num_int - 1
	session['week_viewing'] = week_num

	return str(week_num)


@app.route('/week/<int:week_num>')
def show_calendar(week_num):

	sort_keys, one_weeks_data = data_filter.render_data(week_num)

	return render_template('calendar.html', keys=sort_keys, a_weeks_data = one_weeks_data)


@app.route('/older')
def show_older():
	"""Checks the session dictionary for the week that is currently being viewed and 
	displays info for the previous week."""
	# First we decrement the week_number in session:
	session['week_viewing'] -= 1

	requested_week = session['week_viewing']
	sort_keys, one_weeks_data = data_filter.render_data(requested_week)

	return render_template('calendar.html', keys=sort_keys, a_weeks_data = one_weeks_data)


@app.route('/newer')
def show_newer():
	"""Checks the session dictionary for the week that is currently being viewed and 
	displays info for the nex week after that."""
	# First we increment the week_number in session:
	session['week_viewing'] += 1

	requested_week = session['week_viewing']
	sort_keys, one_weeks_data = data_filter.render_data(requested_week)

	return render_template('calendar.html', keys=sort_keys, a_weeks_data = one_weeks_data)


@app.route('/day/<day>')
def show_day(day):

	days_data = data_filter.format_data_day(day)
	return render_template('day.html', keys=ORDERED_KEY_LIST_DAY, days_data=days_data)



if __name__ == '__main__': 
	app.run( 
		debug=True, 
		port=8100, 
		ssl_context=('/Users/amandagilmore/GoogleFit/server.crt', 
			'/Users/amandagilmore/GoogleFit/server.key'))