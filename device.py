#!/usr/bin/python

import time;
import paho.mqtt.client as mqtt
import json, time, sys, ssl

light_status = "off"
light_percentage = "0"

host = "AVKHJFJ8T3IVK.iot.eu-west-1.amazonaws.com"
topic = "$aws/things/dummy/shadow/update"

cert_path = "/home/renlin/echo/project/cert/"
root_cert = cert_path + "rootCA.key"
cert_file = cert_path + "certificate.pem.crt"
key_file = cert_path + "private.pem.key"

globalmessage = ""  # to send status back to MQTT
isConnected = False

def get_system_status(data):
    speech_output = "The light is currently " + light_status
    print (speech_output)

def set_system_status(data):
    global light_status
    speech_output = ""
    status = data["slots"]["status"]["value"]

    if status in ["on", "off"]:
        light_status = status
        speech_output = "The light is set " + status
    else:
        speech_output = "Unknown status " + status
    print (speech_output)

def get_system_percentage(data):
    speech_output = "The light is currently " + light_percentage + "%"
    print (speech_output)

def set_system_percentage(data):
    global light_percentage
    speech_output = ""

    percentage = data["slots"]["percentage"]["value"]
    print (percentage)
    if int (percentage) >= 0 or int (percentage) <= 100:
        light_percentage = percentage
        speech_output = "The light is set to " + light_percentage + "%"
    else:
        speech_output = "The light is out of range " + light_percentage

    print (speech_output)

def get_system_date(data):
    speech_output = "The date is " + time.strftime("%c")
    print (speech_output)

def get_welcome_response(data):
    speech_output = "Hello World!"
    print (speech_output)

dispatch = {
        'GetLightStatus': get_system_status,
        'SetLightStatus': set_system_status,
        'SetPercentage': set_system_percentage,
        'GetPercentage': get_system_percentage,
        'GetDate': get_system_date,
        'AMAZON.HelpIntent': get_welcome_response
        }

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    isConnected = True
    # Subscribing in on_connect() means that if we lose the connection and      
    # reconnect then subscriptions will be renewed.    
    client.subscribe(topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    data = msg.payload.decode ("utf-8")
    data = json.loads(data)
    # INTENT
    if "name" in data:
        command = data["name"]
        if command in dispatch:
            dispatch[command](data)
        else:
            print ("unknown command: %s" % command)
    else:
        print ("unknow message")
        print (data)

client = mqtt.Client(client_id="device.py")
client.on_connect = on_connect
client.on_message = on_message
client.tls_set(root_cert,
               certfile = cert_file,
               keyfile = key_file,
               cert_reqs=ssl.CERT_REQUIRED,
               tls_version=ssl.PROTOCOL_TLSv1_2,
               ciphers=None)

client.connect(host, 8883, 60)

run = True

try:
    while run:
        client.loop()
        time.sleep(0.1)
        #mypayload = 'response'
        #client.publish (topic, mypayload)

except KeyboardInterrupt:
    print ("Bye Bye!")

