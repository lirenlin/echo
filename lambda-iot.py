import json
import time
import boto3

client = boto3.client('iot-data', region_name='eu-west-1')
topic = r"$aws/things/dummy/shadow/update"

initialized = False
deviceDict = {}

class Device:
	deviceList = []
	def __init__ (self, id, name, dimmable, status=0):
		# Those attribute are read-only
		self.deviceID = id;
		self.name = name;
		self.dimmable = dimmable;

		self.status = status;
		self.dim = 0;

	def setStatus (self, status):
		self.status = status
	def getStatus (self):
		return self.status

	def getID (self):
		return self.deviceID

	def getDim (self):
		return self.dim
	def dimDevice (self, dim):
		self.dim = dim

	def validDevice (self):
		return (self.deviceID >= 0)
	def isDimmable (self):
		return self.dimmable
	def __str__ (self):
		string = ""
		status = ["off", "on"][self.status]
		if self.deviceID  == 0:
			for dev in Device.deviceList[1:]:
				string += dev.__str__ () + ' '
		else:
			string = "deviceID: %s, Name: %s, Status: %s, Dimmable: %d, dim: %d" % \
					(self.deviceID, self.name[0], status, self.dimmable, self.dim)
		return string

	def alexa_str (self):
		string = ""
		status = ["off", "on"][self.status]
		if self.deviceID  == 0:
			for dev in Device.deviceList[1:]:
				string += dev.alexa_str () + ' '
		else:
			if self.isDimmable () and self.dim > 0:
				string = "%s is currently %s, %d percent." % (self.name[0], status, self.dim)
			else:
				string = "%s is currently %s." % (self.name[0], status)
		return string			

def init_device_list ():
	global initialized
	global deviceDict

	if initialized:
		return
	else:
		initialized = True
	

	Device.deviceList = list ()
	deviceDict = dict ()

	name = ["all device", "all"]
	Device.deviceList.append (Device (0, name, 0))

	name = ["kitchen light", "kitchen"]
	Device.deviceList.append (Device (1, name, 0))

	name = ["living room light", "livingroom light", "living"]
	Device.deviceList.append (Device (2, name, 0))

	# this is dimmable
	name = ["bedroom light", "bed room light", "bedroom"]
	Device.deviceList.append (Device (3, name, 1))

	name = ["coffee maker", "coffee", "coffeemaker"]
	Device.deviceList.append (Device (4, name, 0))


        deviceDict = {"kitchen light": 1, "kitchen": 1,
                "living room light": 2, "livingroom light": 2, "living": 2, 
                "bedroom light": 3, "bed room light": 3, "bedroom": 3,
                "coffee maker": 4, "coffee": 4, "coffeemaker": 4,
		"all device": 0, "all": 0}


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
    init_device_list ();
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
    msg = build_push_msg ("stop", 0, 0, 0)

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

    global deviceDict

    if "device" in intent["slots"]:
        device_str = intent["slots"]["device"]["value"]
        device_str = device_str.lower()

        if device_str in deviceDict:
            device = Device.deviceList[deviceDict[device_str]];
	    if device:
	        speech_output = device.alexa_str ()
	    else:
                speech_output = "unknown device"
        else:
            speech_output = "unknown device"
    else:
        speech_output = "please tell me which device"
        should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def set_system_status(intent):
    session_attributes = {}
    card_title = "Smart home Status"
    speech_output = ""
    reprompt_text = ""
    should_end_session = False

    global deviceDict

    deviceID = -1;
    status = None;

    status_str = None;
    device_str = None;

    # get proper device
    if "device" in intent["slots"]:
        device_str = intent["slots"]["device"]["value"]
        device_str = device_str.lower()

        if device_str in deviceDict:
            device = Device.deviceList[deviceDict[device_str]]

            # get proper status
            if "status" in intent["slots"]:
                status_str = intent["slots"]["status"]["value"]
                status_str = status_str.lower()
                if status_str == "on":
                    status = 1
	            device.setStatus (status)
                elif status_str == "off":
                    status = 0
	            device.setStatus (status)
                else:
                    reprompt_text = "Unknown status, Only on or off is accepted"
            else:
                   reprompt_text = "please tell me what to do with %s" % (device_str)

        else:
            reprompt_text = "Unknown device %s." % (device_str)
    else:
        reprompt_text = "please tell me which device"

    # If any information is missing, report to the user.
    if device == None or status == None:
        reprompt_text = "please give me proper instruction"
        return build_response(session_attributes,
                build_speechlet_response(card_title, speech_output,
                    reprompt_text, should_end_session))

    speech_output = "The %s is set %s" %(device_str, status_str)
    should_end_session = True

    # build a simple message for the device
    msg = build_push_msg (intent["name"], device.getID (), status, 0)

    return mqtt_publish (msg, session_attributes, card_title,
            speech_output, reprompt_text, should_end_session)

def set_system_percentage(intent):
    session_attributes = {}
    card_title = "Smart home Status"
    speech_output = ""
    reprompt_text = ""
    should_end_session = False
    device = None
    error = True

    global deviceDict

    if "dimdevice" in intent["slots"]:
        device_str = intent["slots"]["dimdevice"]["value"]
	device_str = device_str.lower ()

        if device_str in deviceDict:
	    device = Device.deviceList[deviceDict[device_str]]
	    if device.isDimmable () == 0:
                speech_output = "%s is not dimmable" % (device_str)
		device = None
    	    else:
                if "percentage" in intent["slots"]:
                    light_percentage = int (intent["slots"]["percentage"]["value"])
		    print light_percentage
		    if light_percentage < 0 or light_percentage > 100:
			speech_output = "%d percent is too large for %s, please give a number between 1 percent and 100 percent" \
					    % (light_percentage, device_str)
		    else:
                    	speech_output = "%s is set to %d percent" % (device_str, light_percentage)
		    	device.dimDevice (light_percentage)
			error = False
                else:
                    reprompt_text = "please tell me how much to dim"
	else:
	    speech_output = "unknown smart device"
    else:
        reprompt_text = "please tell me which smart device"


    if error == False:
        # build a simple message for the device
        should_end_session = True
        msg = build_push_msg (intent["name"], device.getID (), device.getStatus (), device.getDim ())
        return mqtt_publish (msg, session_attributes, card_title, speech_output,
            reprompt_text, should_end_session)
    else:
        reprompt_text = "please give me proper instruction"
        return build_response(session_attributes,
                build_speechlet_response(card_title, speech_output,
                    reprompt_text, should_end_session))

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

def build_push_msg(intent, id, status, dim):
    return {
        "name": intent,
        "deviceID": id,
        "status": status,
        "dim": dim
    }
