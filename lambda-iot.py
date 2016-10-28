import json
import time
import boto3

client = boto3.client('iot-data', region_name='eu-west-1')
topic = r"$aws/things/dummy/shadow/update"

light_status = "OFF"
light_percentage = "0"

def lambda_handler(event, context):
    if (event["session"]["application"]["applicationId"] !=
    "amzn1.ask.skill.fac0b3c8-60c7-45c5-921c-d8141f840e73"):
        raise ValueError("Invalid Application ID")

    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]},
                event["session"])

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
    print intent_name

    if intent_name == "GetLightStatus":
        return get_system_status(intent)
    elif intent_name == "SetLightStatus":
        return set_system_status(intent)
    elif intent_name == "GetPercentage":
        return get_system_percentage(intent)
    elif intent_name == "SetPercentage":
        return set_system_percentage(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif (intent_name == "AMAZON.CancelIntent"
            or intent_name == "AMAZON.StopIntent"):
        return handle_session_end_request(intent)
    else:
        return get_unknown_response ()
        #raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print "Ending session."
    # Cleanup goes here...

def handle_session_end_request(intent):
    session_attributes = {}
    card_title = "i-ideal"
    speech_output = "Thank you for using the i-ideal skill.  See you next time!"
    reprompt_text = ""
    should_end_session = True
    msg = {"name": "stop"}

    return mqtt_publish (msg, session_attributes, card_title, speech_output,
        reprompt_text, should_end_session)

def get_welcome_response():
    session_attributes = {}
    card_title = "i-ideal"
    speech_output = "Welcome to the i-ideal smart light system. "\
    "You can ask me the information about the light"
    reprompt_text = "Please ask me for the status"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_unknown_response():
    session_attributes = {}
    card_title = "i-ideal"
    speech_output = "unknown intent"
    reprompt_text = "Please ask me proper question"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_system_status(intent):
    session_attributes = {}
    card_title = "Light System Status"
    reprompt_text = ""
    should_end_session = False

    speech_output = "The light is currently " + light_status

    return mqtt_publish (intent, session_attributes, card_title, speech_output,
            reprompt_text, should_end_session)

def set_system_status(intent):
    session_attributes = {}
    card_title = "Light System Status"
    speech_output = ""
    reprompt_text = ""
    should_end_session = False
    global light_status

    status = None;
    num = None;

    # get proper status
    if "status" in intent["slots"]:
        status_str = intent["slots"]["status"]["value"]
        status_str = status_str.lower()
        if status_str in ["on", "off"]:
            light_status = status_str
            status = status_str
        else:
            speech_output = "Unknown status, Only on or off is accepted"
    else:
        speech_output = "please tell me what to do with the light"

    # get proper number
    if "num" in intent["slots"]:
        num_str = intent["slots"]["num"]["value"]
        num_str = num_str.lower()
        dic = {"first": 1, "1st": 1, "1": 1,
                "second": 2, "2nd": 2, "2": 2,
                "third": 3, "3rd": 3, "3": 3,
                "fourth": 4, "4th": 4, "4":4,
                "last": 4, "all": 5}

        if num_str in dic:
            num = num_str;
            # make the code in device simpler
            intent["slots"]["num"]["value"] = dic[num]
        else:
            speech_output = "Unknown light. Only 1 to 4 light is available"
    else:
        speech_output = "please tell me which light"

    # If any information is missing, report to the user.
    if num == None or status == None:
        return build_response(session_attributes,
                build_speechlet_response(card_title, speech_output,
                    reprompt_text, should_end_session))

    speech_output = "The %s light is set %s" %(num, status)
    should_end_session = True

    # build a simple message for the device
    msg = {"name": intent["name"],
            "status": intent["slots"]["status"]["value"],
            "num": intent["slots"]["num"]["value"]}

    return mqtt_publish (msg, session_attributes, card_title,
            speech_output, reprompt_text, should_end_session)

def get_system_percentage(intent):
    session_attributes = {}
    card_title = "Light System Status"
    reprompt_text = ""
    should_end_session = True

    speech_output = "The light is currently " + light_percentage + "%"

    return mqtt_publish (intent, session_attributes, card_title, speech_output,
            reprompt_text, should_end_session)

def set_system_percentage(intent):
    session_attributes = {}
    card_title = "Light System Status"
    speech_output = "I am not sure what you mean, please do it again"
    reprompt_text = ""
    should_end_session = True
    global light_percentage

    if "percentage" in intent["slots"]:
        light_percentage = intent["slots"]["percentage"]["value"]
        speech_output = "The light is set to " + light_percentage + "%"

    return mqtt_publish (intent, session_attributes, card_title, speech_output,
            reprompt_text, should_end_session)

def mqtt_publish (intent, session_attributes, card_title, speech_output,
        reprompt_text, should_end_session):

    strIntent = json.dumps (intent)
    client.publish (topic=topic, qos=1, payload=strIntent)
    print strIntent

    return build_response (session_attributes, build_speechlet_response(
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
