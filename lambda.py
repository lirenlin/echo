import json
import time

light_status = "OFF"
light_percentage = "0"

def lambda_handler(event, context):
    if (event["session"]["application"]["applicationId"] !=
    "amzn1.ask.skill.fac0b3c8-60c7-45c5-921c-d8141f840e73"):
        raise ValueError("Invalid Application ID")
    
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def on_session_started(session_started_request, session):
    print "Starting new session."

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    if intent_name == "GetLightStatus":
        return get_system_status()
    elif intent_name == "SetLightStatus":
        return set_system_status(intent)
    elif intent_name == "GetPercentage":
        return get_system_percentage()
    elif intent_name == "SetPercentage":
        return set_system_percentage(intent)
    elif intent_name == "GetDate":
        return get_system_date()
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print "Ending session."
    # Cleanup goes here...

def handle_session_end_request():
    card_title = "BART - Thanks"
    speech_output = "Thank you for using the BART skill.  See you next time!"
    should_end_session = True

    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_welcome_response():
    session_attributes = {}
    card_title = "BART"
    speech_output = "Welcome to the Alexa BART skill. "\
    "You can ask me the information about the light"
    reprompt_text = "Please ask me for the status"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_system_status():
    session_attributes = {}
    card_title = "Light System Status"
    reprompt_text = ""
    should_end_session = False

    speech_output = "The light is currently OFF"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def set_system_status(intent):
    session_attributes = {}
    card_title = "Light System Status"
    speech_output = "I am not sure what you mean, please do it again"
    reprompt_text = ""
    should_end_session = False

    if "status" in intent["slots"]:
        status = intent["slots"]["status"]["value"]
        if status in ["on", "off"]:
            light_status = status
            speech_output = "The light is set " + status
        else:
            speech_output = "Unknown status " + status

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_system_percentage():
    session_attributes = {}
    card_title = "Light System Status"
    reprompt_text = ""
    should_end_session = False

    speech_output = "The light is currently " + light_percentage + "%"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def set_system_percentage(intent):
    session_attributes = {}
    card_title = "Light System Status"
    speech_output = "I am not sure what you mean, please do it again"
    reprompt_text = ""
    should_end_session = False

    if "percentage" in intent["slots"]:
        percentage = intent["slots"]["percentage"]["value"]
        light_percentage = percentage
        speech_output = "The light is set to " + light_percentage + "%"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_system_date():
    session_attributes = {}
    card_title = "Light System Status"
    reprompt_text = ""
    should_end_session = False

    speech_output = "The date is " + time.strftime("%c")

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }

