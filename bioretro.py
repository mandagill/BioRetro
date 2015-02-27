""""This will contain the Flask server and routes for the BioRetro"""
import Fit_OAuth as foa
from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for, render_template
from flask.json import jsonify
import os


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

	some_data = foa.fetch_data()
	print some_data.content
	return some_data.content


if __name__ == '__main__': 
	app.run( 
		debug=True, 
		port=8100, 
		ssl_context=('/Users/amandagilmore/GoogleFit/server.crt', 
			'/Users/amandagilmore/GoogleFit/server.key'))