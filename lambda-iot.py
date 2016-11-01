import json
import time
import boto3

client = boto3.client('iot-data', region_name='eu-west-1')
topic = r"$aws/things/dummy/shadow/update"

device_status = "OFF"
light_percentage = "0"

def lambda_handler (event, context):
    appID = event["session"]["application"]["applicationId"]
    if (appID != "amzn1.ask.skill.fac0b3c8-60c7-45c5-921c-d8141f840e73"
            and appID != "amzn1.ask.skill.472810a7-e6e9-4d80-98bb-741495bb3a1b"
            and appID != "amzn1.ask.skill.dd916f2d-6443-4fa6-b9ff-3dc547fe0c0e"):
        raise ValueError("Invalid Application ID")

    if event["session"]["new"]:
        on_session_started ({"requestId": event["request"]["requestId"]},
                event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def on_session_started (session_started_request, session):
    print "Starting new session."

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]
    print intent_name

    if intent_name == "GetDeviceStatus":
        return get_system_status(intent)
    elif intent_name == "SetDeviceStatus":
        return set_system_status(intent)
    elif intent_name == "GetDeviceDim":
        return get_system_percentage(intent)
    elif intent_name == "SetDeviceDim":
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
    speech_output = "Welcome to the i-ideal smart control system. "\
    "You can ask me the information about the smart device"
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
    card_title = "Smart home Status"
    reprompt_text = ""
    speech_output = ""
    should_end_session = True
    device = None

    if "device" in intent["slots"]:
        device = intent["slots"]["device"]["value"]
        speech_output = "%s is currently %" %(device, device_status)
    else:
        speech_output = "please tell me which smart device"
        should_end_session = False

    return mqtt_publish (intent, session_attributes, card_title, speech_output,
            reprompt_text, should_end_session)

def set_system_status(intent):
    session_attributes = {}
    card_title = "Smart home Status"
    speech_output = ""
    reprompt_text = ""
    should_end_session = False
    global device_status

    status = None;
    deviceID = None;

    # get proper status
    if "status" in intent["slots"]:
        status_str = intent["slots"]["status"]["value"]
        status_str = status_str.lower()
        if status_str in ["on", "off"]:
            device_status = status_str
            status = status_str
        else:
            speech_output = "Unknown status, Only on or off is accepted"
    else:
        speech_output = "please tell me what to do with smart device"

    # get proper device
    if "device" in intent["slots"]:
        device_str = intent["slots"]["device"]["value"]
        device_str = device_str.lower()
        dic = {"kitchen light": 1, "kitchen": 1,
                "living room light": 2, "livingroom light": 2, "living": 2, 
                "bedroom light": 3, "bed room light": 3, "bedroom": 3,
                "coffee maker": 4, "coffee": 4, "coffeemaker": 4,
                "all": 5}

        if device_str in dic:
            device = device_str;
            # make the code in device simpler
            intent["slots"]["device"]["value"] = dic[device]
        else:
            speech_output = "Unknown device. Only 1 to 4 light is available"
    else:
        speech_output = "please tell me which device"

    # If any information is missing, report to the user.
    if device == None or status == None:
        reprompt_text = "please give me proper instruction"
        return build_response(session_attributes,
                build_speechlet_response(card_title, speech_output,
                    reprompt_text, should_end_session))

    speech_output = "The %s is set %s" %(device, status)
    should_end_session = True

    # build a simple message for the device
    msg = {"name": intent["name"],
            "status": intent["slots"]["status"]["value"],
            "num": intent["slots"]["device"]["value"]}

    return mqtt_publish (msg, session_attributes, card_title,
            speech_output, reprompt_text, should_end_session)

def get_system_percentage(intent):
    session_attributes = {}
    card_title = "Smart home Status"
    speech_output = ""
    reprompt_text = ""
    should_end_session = True
    device = None

    if "device" in intent["slots"]:
        device = intent["slots"]["device"]["value"]
        speech_output = "%s is currently %s \%" % (device, light_percentage)
    else:
        speech_output = "please tell me which smart device"
        should_end_session = False


    return mqtt_publish (intent, session_attributes, card_title, speech_output,
            reprompt_text, should_end_session)

def set_system_percentage(intent):
    session_attributes = {}
    card_title = "Smart home Status"
    speech_output = ""
    reprompt_text = ""
    should_end_session = True
    global light_percentage
    device = None

    if "device" in intent["slots"]:
        device = intent["slots"]["device"]["value"]
        if "percentage" in intent["slots"]:
            light_percentage = intent["slots"]["percentage"]["value"]
            speech_output = "%s is set to %d\%" (device, light_percentage)
        else:
            speech_output = "please tell me dim"
            should_end_session = False
    else:
        speech_output = "please tell me which smart device"
        should_end_session = False

    return mqtt_publish (intent, session_attributes, card_title, speech_output,
            reprompt_text, should_end_session)

def mqtt_publish (intent, session_attributes, card_title, speech_output,
        reprompt_text, should_end_session):

    strIntent = json.dumps (intent)
    client.publish (topic=topic, qos=1, payload=strIntent)
    print strIntent

    return build_response (session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def build_speechlet_response (title, output, reprompt_text, should_end_session):
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
