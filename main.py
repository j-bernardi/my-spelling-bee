"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""
from __future__ import print_function
import random
import urllib2

word_site = "http://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain"

def getDictionary(word_site):
    response = urllib2.urlopen(word_site)
    txt = response.read()
    return txt.splitlines()

def getRandomWord(words):
    randomInt = random.randint(0,len(words)-1)
    return words[randomInt]
    
words = getDictionary(word_site)


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
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

# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {"streak" : 0}
    card_title = "Welcome"
    speech_output = "Welcome to my spelling bee. " \
                    "Do you want me to list your options"
    
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    
    reprompt_text = "Tell me what to do or tell me to list your options"
    
    should_end_session = False
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def list_options(intent, session):
    
    session_attributes = {"streak" : 0}
    speech_output = "Ask me to give you a spelling test. Or ask to be tested on a certain word. "
    reprompt_text = speech_output
    should_end_session = False
    
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def handle_session_end_request(session):
    streak = session['attributes']['streak']
    if (streak == 1):
        word = "word."
    else:
        word = "words."
    card_title = "Session Ended"
    speech_output = "Thank you for practicing spelling with me. " \
                    "Your last streak was " + str(streak) + " " + word \
                    + " Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def spelling_test(intent,session):

    testWord = getRandomWord(words)
    streak = session['attributes']['streak']
    session_attributes = {"testWord" : testWord, "counter" : 0, "isSpellingTest" : True, "streak" : streak}
    speech_output = "Say - skip - or spell the word " + testWord
    reprompt_text = speech_output
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def repeat_word(intent, session) :
    testWord = session['attributes']['testWord']
    #when repeating a word you just want to keep the previous value of isSpellingTest
    isSpellingTest = session['attributes']['isSpellingTest']
    streak = session['attributes']['streak']
    session_attributes = {"testWord" : testWord, "counter" : 0, "isSpellingTest" : isSpellingTest, "streak" : streak}
    speech_output = "Let's try again. Say -skip- or spell the word " + testWord
    reprompt_text = speech_output
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def skip_word(intent,session):
    testWord = getRandomWord(words)
    streak = session['attributes']['streak']
    if (streak == 1):
        word = "word."
    else:
        word = "words."
    session_attributes = {"testWord" : testWord, "counter" : 0, "isSpellingTest" : True, "streak" : 0}
    speech_output = "Your last streak was " + str(streak) + " " +  word + " Say - skip - or spell the word " + testWord
    reprompt_text = speech_output
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def any_word(intent,session):
    testWord = intent['slots']['AnyWord']['value']
    session_attributes = {"testWord" : testWord, "counter" : 0, "isSpellingTest" : False, "streak" : 0}
    speech_output = "How do you spell. " + testWord
    reprompt_text = speech_output
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def spelling_attempt(intent, session):
    
    session_attributes = {}
    #the letter
    letter = intent['slots']['Letter']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id'] 
    #letter = intent['slots']['Letter']['value']
    counter = session['attributes']['counter']
    testWord = session['attributes']['testWord']
    isSpellingTest = session['attributes']['isSpellingTest']
    streak = session['attributes']['streak'] 
    reprompt_text = None 
    should_end_session = False
    
    if str(letter).lower() == testWord[counter].lower():
        
        counter = counter + 1
        #session_attributes = {"testWord" : testWord, "counter" : counter, "isSpellingTest" : isSpellingTest, "streak" : streak}
        
        if counter == len(testWord) :
            streak = streak + 1
            speech_output = "Well done. You spelt " + testWord + " correctly."
            if (isSpellingTest):
                speech_output = speech_output + " Say. Next word. When you're ready for another word."
            else:
                speech_output = speech_output + " Say - stop. Or ask for list options."
        else:
            speech_output = "Ding"
    else:
        #I've changed try me again to try again, change this if it's causing issues
        speech_output = "Sorry, " + str(letter).lower() + " is incorrect. You spelt " + testWord + " incorrectly. You can now - stop - skip - or - try me again."
        counter = 0
    session_attributes = {"testWord" : testWord, "counter" : counter, "isSpellingTest" : isSpellingTest, "streak" : streak}
    return build_response(session_attributes, build_speechlet_response(intent['name'], speech_output, reprompt_text, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "ListOptions":
        return list_options(intent, session)
    elif intent_name == "SpellingTest":
        
        return spelling_test(intent, session)
    elif intent_name == "SpellingAttemptIntent":
        return spelling_attempt(intent, session)
    elif intent_name == "AgainIntent" :
        return repeat_word(intent,session)
    elif intent_name == "SkipWord":
        return skip_word(intent, session)
    elif intent_name == "SingleWord":
        return any_word(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request(session)
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

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
