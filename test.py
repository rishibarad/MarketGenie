import robin_stocks
import getpass

# Login details

def login():
	robin_stocks.login(input("Email: "), getpass.getpass("Password: "))

if __name__ == "__main__":
	login()

	portfolio = robin_stocks.build_holdings()
	for key,value in portfolio.items():
		print(key,value)