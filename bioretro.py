""""This will contain the Flask server and routes for the BioRetro"""
import Fit_OAuth as foa
from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for, render_template
from flask.json import jsonify
import os
import data_filter as data_filter


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


@app.route('/fetch_data')
def data_stub():

	result = data_filter.check_for_new_bpm()

	if result is None:
		return

	print "Data updated!"
	return "Your data has been updated!" #TODO edit the .js to show this to the userself.

# TODO figure out what will be calling this route.
# i.e. what action should result in this calendar being shown?
# /<int:num_week>


# Ultimately this will take a URL parameter of the appropriate 
# week to display data for so we can easily paginate.
# It is currently hardcoded to wk 9 for testing purposes. 
@app.route('/week')
def show_calendar():
	# TODO work out where determine_week gets called and how
	# it gets passed to this function. 
	# week_num = determine_week()
	# list_of_weeks_data = fetch_weeks_data(9)
	a_weeks_data = data_filter.format_data_week([])
	return render_template('calendar.html', a_weeks_data = a_weeks_data)


# TODO this should also take a URL param that is the date string
@app.route('/day/<day>')
def show_day(day):

	ORDERED_KEY_LIST_DAY = [
		'9 am',
		'10 am',
		'11 am',
		'noon',
		'1 pm',
		'2 pm',
		'3 pm',
		'4 pm',
		'5 pm'
	]

	days_data = data_filter.format_data_day()
	return render_template('day.html', keys=ORDERED_KEY_LIST_DAY, days_data=days_data)


if __name__ == '__main__': 
	app.run( 
		debug=True, 
		port=8100, 
		ssl_context=('/Users/amandagilmore/GoogleFit/server.crt', 
			'/Users/amandagilmore/GoogleFit/server.key'))