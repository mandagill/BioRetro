from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for, render_template
from flask.json import jsonify
import os


os.environ['DEBUG'] = '1'

app = Flask(__name__)
app.secret_key = "pleasedon'tmockmethisisfordevonlyNOTAREALKEY"


FIT_CLIENT_ID = os.environ['FIT_CLIENT_ID']
FIT_CLIENT_SECRET = os.environ['FIT_CLIENT_SECRET']
# Hardcoding to localhost until I can sort out deployment
REDIRECT_URI = 'https://localhost:8100/callback'

# These are the OAuth enpoints in the Google Fit API documentation: 
# https://developers.google.com/accounts/docs/OAuth2WebServer
AUTHORIZATION_BASE_URL = 'https://accounts.google.com/o/oauth2/auth'
TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
SCOPE = [
	'https://www.googleapis.com/auth/fitness.body.read'
]


@app.route('/')
def go_home():
	# return render_template('home.html')
	"""Redirects to the OAuth provider. Putting inside the home function per the tutorial here: 
	https://requests-oauthlib.readthedocs.org/en/latest/examples/real_world_example.html#real-example"""

	google = OAuth2Session(FIT_CLIENT_ID, scope=SCOPE, redirect_uri=REDIRECT_URI)
	authorization_url, state = google.authorization_url(AUTHORIZATION_BASE_URL,
		access_type='offline',
		approval_prompt='force')

	session['auth_url'] = authorization_url
	session['oauth_state'] = state

	return redirect(authorization_url)  # redirect(AUTHORIZATION_BASE_URL)


@app.route('/callback', methods=['GET', 'POST'])
def callback():
	"""Retrieving an access token."""
	
	print request.args
	print request

	code = request.args.get('code')

	google = OAuth2Session(FIT_CLIENT_ID, state=request.args.get('state'), redirect_uri=REDIRECT_URI)

	print request.form
	# FIXME: 
	# Need to send params as specified at below URL. Not sure how to get the auth code 
	# and pass it to a different route in my app.
	# https://developers.google.com/accounts/docs/OAuth2InstalledApp#choosingredirecturi
	token = google.fetch_token(
		TOKEN_URL,
		client_id = FIT_CLIENT_ID,
		client_secret = FIT_CLIENT_SECRET,
		code=code )

	session['oauth_token'] = token

	return render_template('okauth.html')


@app.route('/okauth')
def got_token():

	return render_template('/okauth.html')


if __name__ == '__main__': 
	app.run( 
		debug=True, 
		port=8100, 
		ssl_context=('/Users/amandagilmore/GoogleFit/server.crt', 
			'/Users/amandagilmore/GoogleFit/server.key'))



