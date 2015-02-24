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
REDIRECT_URI = 'https://localhost:5000/callback'

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
	https://requests-oauthlib.readthedocs.org/en/latest/examples/real_world_example.html#real-example
	The tutorial for Google specifically created the remote object *outside* the function, here:
	https://requests-oauthlib.readthedocs.org/en/latest/examples/google.html"""

	google = OAuth2Session(FIT_CLIENT_ID, scope=SCOPE, redirect_uri=REDIRECT_URI)
	authorization_url, state = google.authorization_url(AUTHORIZATION_BASE_URL,
		access_type='offline',
		approval_prompt='force')

	print "this is the value of 'state' after calling Google: ", state

	session['oauth_state'] = state
	# import pdb; pdb.trace()

	print "this is the value of 'state' after the API call", state

	return redirect(authorization_url)  # redirect(AUTHORIZATION_BASE_URL)


@app.route('/callback', methods=['GET'])
def callback():
	"""Retrieving an access token."""
	
	google = OAuth2Session(FIT_CLIENT_ID, state=session['oauth_state'])
	token = google.fetch_token(
		TOKEN_URL,
		client_secret=FIT_CLIENT_SECRET,
		authorization_response=request.url)

	session['oauth_token'] = token

	return redirect('/okauth.html')


# This was from another tutorial, hanging on to the code for reference but likely will delete. 


# from flask import render_template
# from flask.ext.login import current_user
# from flask.views import MethodView

# from myapp import app

# flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=OAUTH_SCOPE)

# class Index(MethodView):
#     def get(self):
#         # check if user is logged in
#         if not current_user.is_authenticated():
#             return app.login_manager.unauthorized()

#         return render_template('index.html')	

if __name__ == '__main__': 
	app.run( 
		debug=True, 
		port=8100, 
		ssl_context=('./Users/amandagilmore/GoogleFit/server.crt', 
			'./Users/amandagilmore/GoogleFit/server.key'))



