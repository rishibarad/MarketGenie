# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import boto3

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

import yfinance as yf
from datetime import date, timedelta
import requests
# from ask_sdk_dynamodb.adapter import DynamoDbAdapter, user_id_partition_keygen

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# dynamo_client = DynamoDbAdapter(table_name="MarketGenieDynamo", partition_key_name="userId", partition_keygen=user_id_partition_keygen, sort_key_name="Ticker", create_table=False, dynamodb_resource=dynamodb)
#dynamodb = boto3.resource('dynamodb', region_name='us-east-2')

#def add_watchList(userID, ticker, dynamodb):
    #
    # attr = {
    #     'userId' : userID
    #     'Ticker': ticker
    # }
    # dynamo_client.save_attributes(request_envelope=handler_input.request_envelope, attributes=attr)
 #   if not dynamodb:
    #    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    
    #console.log("NOTE: started add watchlist")
    
  #  watchTable = dynamodb.Table('MarketGenieDynamo')
   # response = watchTable.put_item(
   #   Item={
    #        'userId': userID,
    #        'Ticker': ticker
   #     }
   # ) 
    # except ClientError as e:
        # print(e.response)
        # return e.response['Error']['Code']  
        
  #  return True        

# def remove_watchList(userID, ticker, dynamodb=None):
#     try:
#         # attr = {
#         #     'userId' : userID
#         #     'Ticker': ticker
#         # }
#         # self.dynamo_client.delete_attributes(request_envelope=handler_input.request_envelope, attributes=attr)
#         response = watchTable.delete_item(
#           Item={
#                 'userId': userID,
#                 'Ticker': ticker
#             }
#         ) 
#     except ClientError as e:
#         print(e.response)
#         return e.response['Error']['Code']        
#     return True

def get_name(ticker):
    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(ticker)

    result = requests.get(url).json()

    for x in result['ResultSet']['Result']:
        if x['symbol'] == ticker:
            return x['name'].replace('&', ' and ')
    return "I'm sorry I couldn't find the name you were looking for!"

def get_ticker(handler_input):
    ticker_slot = ask_utils.get_slot(handler_input=handler_input, slot_name="ticker")
    ticker_resolution = ticker_slot.resolutions.resolutions_per_authority[0]
    return ticker_resolution.values[0].value.name


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hi! Welcome to the Genie! You can ask a simple question like what a certain company ticker's price is at or you can add or remove a company from your watchlist!"
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class StockPriceIntentHandler(AbstractRequestHandler):
    """Handler for Stock Price Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("StockPriceIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        # Get resolution
        ticker = get_ticker(handler_input)
        
        # Get stock data and report
        tomorrow = date.today() + timedelta(days=1)
        stock_data = yf.download(ticker, start=date.today(), end=tomorrow)

        company = get_name(ticker)
        price = stock_data.iloc[0][3]
        dollars = int(price)
        cents = int((price - dollars) * 100)

        speak_output = company + " is at " + str(dollars) + " dollars and " + str(cents) + " cents."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )
    
class AddWatchlistIntentHandler(AbstractRequestHandler):
    """Handler for Add Watchlist Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AddWatchlistIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        # Get resolution
        ticker = get_ticker(handler_input)
        company = get_name(ticker)
        user_id = ask_utils.get_user_id(handler_input)
        
        
        # user_id = ask_utils.get_user_id(handler_input)
        speak_output = "<amazon:emotion name=\"excited\" intensity=\"high\">You invoked the add watchlist intent!</amazon:emotion>"
        
        #if (add_watchList(user_id, ticker, dynamodb)):
        #    speak_output = "<amazon:emotion name=\"excited\" intensity=\"high\">I've added {} to your watchlist!</amazon:emotion>".format(company)
        #else:
        #    speak_output = "I'm sorry, I couldn't add {} to your watchlist".format(company)
            
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class RemoveWatchlistIntentHandler(AbstractRequestHandler):
    """Handler for Remove Watchlist Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("RemoveWatchlistIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You invoked the remove watchlist intent!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class ReportWatchlistIntentHandler(AbstractRequestHandler):
    """Handler for Report Watchlist Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ReportWatchlistIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You invoked the report watchlist intent!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class CheckWatchlistIntentHandler(AbstractRequestHandler):
    """Handler for Check Watchlist Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("CheckWatchlistIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You invoked the check watchlist intent!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )
    
class PortfolioIntentHandler(AbstractRequestHandler):
    """Handler for Portfolio Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("PortfolioIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You invoked the portfolio intent!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        tomorrow = date.today() + timedelta(days=1)
        msft = yf.download("MSFT", start=date.today(), end=tomorrow)
        speak_output = "Microsoft closed today at " + str(round(msft.iloc[0][3], 2))

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can ask a simple question like what a certain company ticker's price is at or you can add or remove a company from your watchlist!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

# Skill ID check
sb.skill_id = "amzn1.ask.skill.709723c9-fbae-4771-b7c4-c156ca5d821b"

# Launcher
sb.add_request_handler(LaunchRequestHandler())

# Custom intents
sb.add_request_handler(StockPriceIntentHandler())
sb.add_request_handler(AddWatchlistIntentHandler())
sb.add_request_handler(RemoveWatchlistIntentHandler())
sb.add_request_handler(ReportWatchlistIntentHandler())
sb.add_request_handler(CheckWatchlistIntentHandler())
sb.add_request_handler(PortfolioIntentHandler())
sb.add_request_handler(HelloWorldIntentHandler())

# Default intents
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()