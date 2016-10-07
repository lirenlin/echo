#!/usr/bin/python

import time;
import paho.mqtt.client as mqtt
import json, time, sys, ssl

lights = 13
feeder = 11

host = "https://avkhjfj8t3ivk.iot.eu-west-1.amazonaws.com"
topic = "$aws/things/dummy/shadow/update"

cert_path = "/home/renlin/echo/project/cert/"
root_cert = cert_path + "rootCA.key"
cert_file = cert_path + "certificate.pem.crt"
key_file = cert_path + "private.pem.key"

globalmessage = ""  # to send status back to MQTT
isConnected = False

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    isConnected = True
    # Subscribing in on_connect() means that if we lose the connection and      
    # reconnect then subscriptions will be renewed.    
    client.subscribe(topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    data = json.loads(str(msg.payload))
    # INTENT
    if "name" in data:
        command = data["name"]
        if command == "GetLightStatus":
            print command
        if command == "SetLightStatus":
            print command
        if command == "SetPercentage":
            print command
        if command == "GetPercentage":
            print command
        if command == "GetDate":
            print command
        if command == "AMAZON.HelpIntent":
            print command
        if command == "AMAZON.StopIntent":
            print command

client = mqtt.Client(client_id="device.py")
client.on_connect = on_connect
client.on_message = on_message
client.on_log = on_log
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
        time.sleep(1)

except KeyboardInterrupt:
    print "Bye Bye!"
