import getpass
import robin_stocks as robin
import os
import pickle
# import yfinance as yahoo
# dependencies must be added to requirements.txt Alexa file

def login():
	# hoping that extended session (30 days) works properly with Robinhood api. 86400 (1 day) is default
	session = robin.login(expiresIn=86400*30)
	print(session)


if __name__ == "__main__":
	login()

	portfolio = robin.build_holdings()
	for key,value in portfolio.items():
		print(key,value)

	aapl_price = robin.stocks.get_latest_price('AAPL', includeExtendedHours=True)
	print("Apple Latest Price:", aapl_price[0])
	# robin.logout()