import json
import boto3
from datetime import date, timedelta
import yfinance as yf
import pandas as pd
import numpy as n
from botocore.vendored import requests
from boto3.dynamodb.conditions import Key

# These are the helper functions 
def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
    
def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Hi! Welcome to the Genie! You can ask a simple question like what a certain company ticker's price is at or you can add or remove a company from your watchlist!"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "I don't know if you heard me, welcome to the Genie!"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
    
def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for using the Genie. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def on_session_started(session_started_request, session):
    """ Called when the session starts.
        One possible use of this function is to initialize specific 
        variables from a previous state stored in an external database
    """
    # Add additional code here as needed
    pass

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    # Dispatch to your skill's launch message
    return get_welcome_response()

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

def get_name(ticker):
    ticker = ticker.upper()
    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(ticker)

    result = requests.get(url).json()

    for x in result['ResultSet']['Result']:
        if x['symbol'] == ticker:
            return x['name'].replace('&', ' and ')
    return None
    
    

def add_watchList(intent, session):
    # ticker = intent['slots']['ticker']['value']
    ticker = intent['slots']['ticker']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']
    #ticker = ticker.upper()
    userID = session['user']['userId']
    
    client = boto3.resource("dynamodb")
    table = client.Table('WatchlistDynamo')
    response = table.put_item(
         Item={
                'userId': userID,
                'Ticker': ticker
           }
    ) 
    return response
    
def remove_watchList(intent, session):
    #ticker = intent['slots']['ticker']['value']
    ticker = intent['slots']['ticker']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']
    #ticker = ticker.upper()
    userID = session['user']['userId']
    
    client = boto3.resource("dynamodb")
    table = client.Table('WatchlistDynamo')
    response = table.delete_item(
         Key={
                'userId': userID,
                'Ticker': ticker
           }
    ) 
    return response

def tickers_from_user(session):
    userID = session['user']['userId']
        
    client = boto3.resource("dynamodb")
    table = client.Table('WatchlistDynamo')
    response = table.query(
        KeyConditionExpression=Key('userId').eq(userID)
    )
    return response

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "AddWatchlistIntent":
        results = add_watchList(intent, session)
        ticker = intent['slots']['ticker']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']
        company = get_name(ticker)
        
        if company:
            if results:
                speech_output = "You have successfully added {} to your watchlist".format(company)
            # elif results != 'ConditionalCheckFailedException':
            #     speech_output = "You've already added {} to your watchlist".format(company)
            else:
                speech_output = "I couldn't add {} to your watchlist".format(company)
            
            reprompt_text = 'Please try again.'
        else:
            speech_output = "I'm sorry I couldn't find that company, please try again"
            reprompt_text = "What company do you want to add to your watchlist?"
            
        session_attributes = {}
        should_end_session = False
        card_title = "Add to watchlist"
            
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
            
    elif intent_name == "RemoveWatchlistIntent":
        results = remove_watchList(intent, session)
        ticker = intent['slots']['ticker']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']
        company = get_name(ticker)
        
        if company:
            if results:
                speech_output = "You have successfully removed {} from your watchlist".format(company)
            # elif results != 'ConditionalCheckFailedException':
            #     speech_output = "You've already added {} to your watchlist".format(company)
            else:
                speech_output = "I couldn't remove {} from your watchlist".format(company)
            
            reprompt_text = 'Please try again.'
        else:
            speech_output = "I'm sorry I couldn't find that company, please try again"
            reprompt_text = "What company do you want to add to your watchlist?"
            
        session_attributes = {}
        should_end_session = False
        card_title = "Remove from watchlist"
            
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
            
    elif intent_name == "StockPriceIntent":
        ticker = intent["slots"]["ticker"]["value"]
        ticker = ticker.upper()
        
        # Get stock data and report
        tomorrow = date.today() + timedelta(days=1)
        stock_data = yf.download(ticker, start=date.today(), end=tomorrow)

        company = get_name(ticker)
        price = stock_data.iloc[0][3]
        dollars = int(price)
        cents = int((price - dollars) * 100)

        speech_output = company + " is at " + str(dollars) + " dollars and " + str(cents) + " cents."
        session_attributes = {}
        should_end_session = False
        card_title = "Stock Price"
        reprompt_text = "I'm sorry I can't get the price of that company right now, please try again"
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
            
    elif intent_name == "CheckWatchlistIntent":
        results = tickers_from_user(session)
        
        if results["Count"] == 1:
            company = get_name(results["Items"][0]["Ticker"])
            speech_output = "The only company in your watchlist is {}".format(company)
        elif results["Count"] > 1:
            companies = []
            for result in results["Items"]:
                ticker = result['Ticker']
                company = get_name(ticker)
                companies.append(company)
                print (company)
            print(*companies)
            speech_output = "The companies in your watchlist are "
            for x in range(len(companies[:-1])):
                speech_output += companies[x] + " "
            else:
                speech_output += "and " + companies[-1]
        else:
            speech_output = "You don't have any companies in your watchlist. To add one say a command such as add a company to my watchlist."
            
        session_attributes = {}
        should_end_session = False
        card_title = "Check Watchlist"
        reprompt_text = "I'm sorry I can't list your watchlist right now, please try again"
        
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
            
    elif intent_name == "ReportWatchlistIntent":
        results = tickers_from_user(session)
        
        if results["Count"] == 1:
            ticker = results["Items"][0]["Ticker"]
            company = get_name(ticker)
            
            tomorrow = date.today() + timedelta(days=1)
            stock_data = yf.download(ticker, start=date.today(), end=tomorrow)
            price = stock_data.iloc[0][3]
            dollars = int(price)
            cents = int((price - dollars) * 100)

            speech_output = company + " is at " + str(dollars) + " dollars and " + str(cents) + " cents."
            
        elif results["Count"] > 1:
            company_prices = []
            for result in results["Items"]:
                ticker = result['Ticker']
                print(ticker)
                company = get_name(ticker)
                tomorrow = date.today() + timedelta(days=1)
                stock_data = yf.download(ticker, start=date.today(), end=tomorrow)
                
                price = stock_data.iloc[0][3]
                dollars = int(price)
                cents = int((price - dollars) * 100)
                dollars = str(dollars)
                cents = str(cents)
                
                company_prices.append(company)
                company_prices.append(dollars)
                company_prices.append(cents)
                company_prices.append(0)
                
            count = 1
            print(*company_prices)
            for x in range(len(company_prices[:-4])):
                if count == 1 and x == 0:
                    speech_output = "{} is at ".format(company_prices[x])
                elif count == 1:
                    speech_output += " {} is at ".format(company_prices[x])
                    
                if count == 2:
                    speech_output += " {} dollars and ".format(company_prices[x]) 
                    
                if count == 3:
                    speech_output += " {} cents, ".format(company_prices[x])
                if count == 4:
                    count = 0
                count += 1
            else:
                speech_output += " and {} is at {} dollars and {} cents.".format(company_prices[-4], company_prices[-3], company_prices[-2])
            
        else:
            speech_output = "You don't have any companies in your watchlist. To add one say a command such as add a company to my watchlist."
            
        session_attributes = {}
        should_end_session = False
        card_title = "Check Watchlist"
        reprompt_text = "I'm sorry I can't list your watchlist right now, please try again"
        
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
            
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("Incoming request...")

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])