import getpass
import robin_stocks as robin
import os
import pickle
# import yfinance as yahoo
# dependencies must be added to requirements.txt Alexa file


# def login():
# 	device_token = robin.generate_device_token()
# 	home_dir = os.path.expanduser("~")
# 	data_dir = os.path.join(home_dir, ".tokens")
# 	if not os.path.exists(data_dir):
# 		os.makedirs(data_dir)
# 	creds_file = "robinhood.pickle"
# 	pickle_path = os.path.join(data_dir, creds_file)
# 	# Challenge type is used if not logging in with two-factor authentication.
# 	challenge_type = "email"
# 	url = robin.urls.login_url()
# 	payload = {
# 		'client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS',
# 		'expires_in': 86400*30,
# 		'grant_type': 'password',
# 		'password': 'meaningless password',
# 		'scope': 'internal',
# 		'username': username,
# 		'challenge_type': challenge_type,
# 		'device_token': device_token
# 	}
#
# 	# If authentication has been stored in pickle file then load it. Stops login server from being pinged so much.
# 	if os.path.isfile(pickle_path):
# 		# If store_session has been set to false then delete the pickle file, otherwise try to load it.
# 		# Loading pickle file will fail if the access_token has expired.
# 		try:
# 			with open(pickle_path, 'rb') as f:
# 				pickle_data = pickle.load(f)
# 				access_token = pickle_data['access_token']
# 				token_type = pickle_data['token_type']
# 				refresh_token = pickle_data['refresh_token']
# 				# Set device_token to be the original device token when first logged in.
# 				pickle_device_token = pickle_data['device_token']
# 				payload['device_token'] = pickle_device_token
# 				# Set login status to True in order to try and get account info.
# 				robin.helper.set_login_state(True)
# 				robin.helper.update_session(
# 					'Authorization', '{0} {1}'.format(token_type, access_token))
# 				# Try to load account profile to check that authorization token is still valid.
# 				res = robin.helper.request_get(
# 					robin.urls.portfolio_profile(), 'regular', payload, jsonify_data=False)
# 				# Raises exception is response code is not 200.
# 				res.raise_for_status()
# 				return ({'access_token': access_token, 'token_type': token_type,
# 						 'expires_in': expiresIn, 'scope': scope,
# 						 'detail': 'logged in using authentication in {0}'.format(creds_file),
# 						 'backup_code': None, 'refresh_token': refresh_token})
# 		except:
# 			print(
# 				"ERROR: There was an issue loading pickle file. Authentication may be expired - logging in normally.")
# 			helper.set_login_state(False)
# 			helper.update_session('Authorization', None)
# 		else:
# 			os.remove(pickle_path)
# 	# 30 day login? default set to 86400s = 1 day. hoping that over 1 day is possible
# 	sessionToken = robin.login(input("Email: "), getpass.getpass("Password: "), expiresIn=(86400*30))
# 	print(sessionToken)
# 	# the access token was generated with login or loaded from pickle file if session was stored.
# 	# current thought: save the access token with Alexa's
# 	print(sessionToken['access_token'])


def login():
	# hoping that extended session (30 days) works properly with Robinhood api
	# 86400 (1 day) is default
	session = robin.login(expiresIn=86400*30)
	print(session)


if __name__ == "__main__":
	login()

	portfolio = robin.build_holdings()
	for key,value in portfolio.items():
		print(key,value)

	# this function works only after attempting a login. interestingly, you can get the login wrong for this to still work
	# but defeats the purpose of no login so switched to yahoo finance
	nio_price = robin.stocks.get_latest_price('NIO', includeExtendedHours=True)
	print(nio_price[0])
	robin.logout()