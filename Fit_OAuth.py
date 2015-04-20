# """ This contains code to authorize the Google Fit API with OAuth, create a session, 
# and retrieve protected data with the resulting session token."""

# from requests_oauthlib import OAuth2Session
# from flask import Flask, request, redirect, session, url_for, render_template
# from flask.json import jsonify
# import os
# import sys

# FIT_CLIENT_ID = os.environ['FIT_CLIENT_ID']
# FIT_CLIENT_SECRET = os.environ['FIT_CLIENT_SECRET']
# REDIRECT_URI = os.environ['REDIRECT_URI']

# # These are the OAuth enpoints in the Google Fit API documentation: 
# # https://developers.google.com/accounts/docs/OAuth2WebServer
# AUTHORIZATION_BASE_URL = 'https://accounts.google.com/o/oauth2/auth'
# TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
# SCOPE = [
# 	'https://www.googleapis.com/auth/fitness.body.read',
# 	'https://www.googleapis.com/auth/fitness.location.read'
# ]

# # These are the required parameters to call the Google Fit API. The base URL is 
# # self-explanatory, and the foo_DATA constants are data stream IDs from which
# # we can fetch data.
# QUERY_BASE_URI = 'https://www.googleapis.com/fitness/v1/users/me/dataSources'
# SPEED_DATA = '/derived:com.google.speed:com.google.android.gms:merge_speed'
# BPM_DATA = '/derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm'


# def go_to_google():
# 	"""Redirects to the OAuth provider. Putting inside the home function per the tutorial here: 
# 	https://requests-oauthlib.readthedocs.org/en/latest/examples/real_world_example.html#real-example"""

# 	google = OAuth2Session(FIT_CLIENT_ID, scope=SCOPE, redirect_uri=REDIRECT_URI)
# 	authorization_url, state = google.authorization_url(AUTHORIZATION_BASE_URL,
# 		approval_prompt='force')

# 	session['auth_url'] = authorization_url
# 	session['oauth_state'] = state

# 	return authorization_url


# def callback(authcode):
# 	"""Retrieving an access token."""

# 	google = OAuth2Session(FIT_CLIENT_ID, state=session['oauth_state'], redirect_uri=REDIRECT_URI)

# 	token = google.fetch_token(
# 		TOKEN_URL,
# 		client_id = FIT_CLIENT_ID,
# 		client_secret = FIT_CLIENT_SECRET,
# 		code=authcode )

# 	session['oauth_token'] = token

# 	# Write some code to time the life of the call
# 	# sys.stdout.write(stuff)

# 	return render_template('okauth.html')


# def fetch_data(startbound, endbound, data_type):
# 	"""Take a parameter from the caller as to what kind of data is desired,
# 	and start/end time parameters (in nanoseconds, since the Google API was clearly 
# 	written by Java programmers) for the desired dataset.

# 	pass string 'speed' for speed data.
# 	pass string 'bpm' for bpm data. """

# 	# Create an OAuth2 session with the token stored in the Flask session:
# 	google = OAuth2Session(FIT_CLIENT_ID, token=session['oauth_token'])
	
# 	# Checks what the desired datatype is:
# 	if data_type == 'bpm':
# 		source = BPM_DATA
# 	elif data_type == 'speed':
# 		source = SPEED_DATA

# 	# Use the caller-supplied parameters to build the HTTP request.
# 	api_call = QUERY_BASE_URI + source + '/datasets' + '/' + startbound + '-' + endbound
# 	api_response = google.get(api_call)

# 	if api_response.status_code == 200:
# 		sys.stdout.write("count#api_returns_200=5")
# 		return api_response.content
# 		# TODO function returns a string; would like to optimize
# 		# this by making it return a dict to avoid repetition 
# 	elif api_response.status_code >= 400 or api_response.status_code < 500:
# 		sys.stdout.write("count#api_returns_4xx=1")
# 		return "This app hasn't been authorized to access your location or body sensor data." 
# 	elif api_response.status_code == 500:
# 		sys.stdout.write("count#api_returns_500=1")
# 		return "The API seems to be unavailable." 
# 	else:
# 		response_code = api_response.status_code
# 		sys.stdout.write("event#api_returns_other=" + str(response_code))
# 		return "There was a problem getting your data from Google. Please check your debug logs."
# 	# import pdb; pdb.set_trace()






