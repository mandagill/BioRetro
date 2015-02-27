""" This will contain the OAuth code"""
# import bioretro? Not sure if I need the FLask stuff in here
from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for, render_template
from flask.json import jsonify
import os


FIT_CLIENT_ID = os.environ['FIT_CLIENT_ID']
FIT_CLIENT_SECRET = os.environ['FIT_CLIENT_SECRET']
# Hardcoding to localhost until I can sort out deployment
REDIRECT_URI = 'https://localhost:8100/callback'

# These are the OAuth enpoints in the Google Fit API documentation: 
# https://developers.google.com/accounts/docs/OAuth2WebServer
AUTHORIZATION_BASE_URL = 'https://accounts.google.com/o/oauth2/auth'
TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
SCOPE = [
	'https://www.googleapis.com/auth/fitness.body.read',
	'https://www.googleapis.com/auth/fitness.location.read'
]


def go_to_google():
	"""Redirects to the OAuth provider. Putting inside the home function per the tutorial here: 
	https://requests-oauthlib.readthedocs.org/en/latest/examples/real_world_example.html#real-example"""

	google = OAuth2Session(FIT_CLIENT_ID, scope=SCOPE, redirect_uri=REDIRECT_URI)
	authorization_url, state = google.authorization_url(AUTHORIZATION_BASE_URL,
		access_type='offline',
		approval_prompt='force')

	session['auth_url'] = authorization_url
	session['oauth_state'] = state

	return authorization_url


def callback(authcode):
	"""Retrieving an access token."""

	google = OAuth2Session(FIT_CLIENT_ID, state=session['oauth_state'], redirect_uri=REDIRECT_URI)

	token = google.fetch_token(
		TOKEN_URL,
		client_id = FIT_CLIENT_ID,
		client_secret = FIT_CLIENT_SECRET,
		code=authcode )

	session['oauth_token'] = token

	return render_template('okauth.html')


def fetch_data():
	"""Getting distance data, currently hardcoded. This will eventually take nanotime start and end parameters, 
	and a datatype parameter so this function knows which API endpoint to call."""

	google = OAuth2Session(FIT_CLIENT_ID, token=session['oauth_token'])

	speed_as_json = google.get("""https://www.googleapis.com/fitness/v1/users/me/dataSources/derived:com.google.speed:com.google.android.gms:merge_speed/datasets/1424839324587000000-1424840224587000000""")

	if speed_as_json.status_code == 200:
		return speed_as_json
	elif speed_as_json.status_code == 403:
		return "This app hasn't been authorized to access your location or body sensor data." 
	else:
		return "There was a problem getting your data from Google. Please check your debug logs."
	# import pdb; pdb.set_trace()






