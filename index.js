var awsIot = require('aws-iot-device-sdk');

var host = "https://avkhjfj8t3ivk.iot.eu-west-1.amazonaws.com";
var topic = "$aws/things/dummy/shadow/update";
var app_id = "amzn1.ask.skill.fac0b3c8-60c7-45c5-921c-d8141f840e73";
var deviceName = "Dummy";

var mqtt_config = {
    "keyPath": "./certs/private.pem.key",
    "certPath": "./certs/cert.pem.crt",
    "caPath": "./certs/rootCA.key",
    "host": host,
    "port": 8883,
    "clientId": deviceName, 
    "region":"us-east-1",
    "debug":true
};

var ctx = null;
var client = null;

// Route the incoming request based on type (LaunchRequest, IntentRequest, etc.)
// The JSON body of the request is provided in the event parameter.
exports.handler = function (event, context) {
    try {
        console.log("event.session.application.applicationId="
                + event.session.application.applicationId);
        ctx = context;

        if (event.session.application.applicationId !== app_id) {
            ctx.fail("Invalid Application ID");
        }

        client = awsIot.device(mqtt_config);

        client.on("connect",function(){ console.log("Connected to AWS IoT"); });


        if (event.session.new) {
            onSessionStarted({requestId: event.request.requestId}, event.session);
        }

        if (event.request.type === "LaunchRequest") {
            onLaunch(event.request, event.session);
        }  else if (event.request.type === "IntentRequest") {
            onIntent(event.request, event.session);
        } else if (event.request.type === "SessionEndedRequest") {
            onSessionEnded(event.request, event.session);
            ctx.succeed();
        }
    } catch (e) {
        console.log("EXCEPTION in handler:  " + e);
        ctx.fail("Exception: " + e);
    }
};

/**
 * Called when the session starts.
 */
function onSessionStarted(sessionStartedRequest, session) {
    console.log("onSessionStarted requestId=" + sessionStartedRequest.requestId
            + ", sessionId=" + session.sessionId);
}


/**
 * Called when the user launches the skill without specifying what they want.
 */
function onLaunch(launchRequest, session, callback) {
    console.log("onLaunch requestId=" + launchRequest.requestId
            + ", sessionId=" + session.sessionId);

    // Dispatch to your skill's launch.
    getWelcomeResponse(callback);
}

/**
 * Called when the user specifies an intent for this skill.
 */
function onIntent(intentRequest, session ) {
    console.log("onIntent requestId=" + intentRequest.requestId
            + ", sessionId=" + session.sessionId);

    var intent = intentRequest.intent,
    intentName = intentRequest.intent.name;

    console.log("REQUEST to string =" + JSON.stringify(intentRequest));
    var validLightIntent = [ "GetLightStatus", "SetLightStatus",
        "GetPercentage", "SetPercentage"];
    var validOtherIntent = ["GetDate", "AMAZON.HelpIntent", 
        "AMAZON.CancelIntent"];

    var callback = null;
    // Dispatch to your skill's intent handlers
    if (validLightIntent.indexOf(intentName) != -1) {
        lightIntent(intent, session);
    }
    else if (validOtherIntent.indexOf(intentName) != -1) {
        otherIntent(intent, session);
    }
    else {
        throw "Invalid intent";
    }

}

/**
 * Called when the user ends the session.
 * Is not called when the skill returns shouldEndSession=true.
 */
function onSessionEnded(sessionEndedRequest, session) {
    console.log("onSessionEnded requestId=" + sessionEndedRequest.requestId
            + ", sessionId=" + session.sessionId);
    // Add cleanup logic here
}

// --------------- Functions that control the skill's behavior -----------------------

function getWelcomeResponse() {
    // If we wanted to initialize the session to have some attributes we could add those here.
    var sessionAttributes = {};
    var cardTitle = "Welcome";
    var speechOutput = "Welcome to the dummy.";

    var repromptText = "Dummy  is ready for command.";
    var shouldEndSession = false;

    ctx.succeed(buildResponse(sessionAttributes,
                buildSpeechletResponse(cardTitle, speechOutput, repromptText,
                    shouldEndSession)));
}

function lightIntent(intent, session, callback) {
    var repromptText = null;
    var sessionAttributes = {};
    var shouldEndSession = false;
    var speechOutput = "";

    repromptText = "Tell me how you want set the lights.";

    var state = intent.slots.state.value;
    var validstates = [ "on", "off" ];

    if (validstates.indexOf(state) == -1)
    {
        speechOutput = "I couldn't understand the state of the lights. ";
        ctx.succeed(buildResponse(sessionAttributes,
                    buildSpeechletResponse(cardTitle, speechOutput,
                        repromptText, shouldEndSession)));
    }
    else
    {
        var cardTitle = "Lights turning " + state;
        speechOutput = "Turning lights " + state;
        mqttPublish(intent, sessionAttributes, cardTitle, speechOutput,
                repromptText, shouldEndSession);
    }
}

function otherIntent(intent, session, callback) {
    var repromptText = null;
    var sessionAttributes = {};
    var shouldEndSession = false;
    var speechOutput = "";

    repromptText = "";

    var state = intent.slots.state.value;
    var validstates = [ "on", "off" ];

    if (validstates.indexOf(state) == -1)
    {
        speechOutput = "I couldn't understand the state of the lights. ";
        ctx.succeed(buildResponse(sessionAttributes,
                    buildSpeechletResponse(cardTitle, speechOutput,
                        repromptText, shouldEndSession)));
    }
    else
    {
        var cardTitle = "Lights turning " + state;
        speechOutput = "Turning lights " + state;
        mqttPublish(intent, sessionAttributes, cardTitle, speechOutput,
                repromptText, shouldEndSession);
    }
}

function mqttPublish(intent, sessionAttributes, cardTitle, speechOutput,
        repromptText, shouldEndSession)
{
    var strIntent = JSON.stringify(intent);
    console.log("mqttPublish:  INTENT text = " + strIntent);

    client.publish(topic, strIntent, function() {
        client.end();
    });

    client.on("close", (function () {
        console.log("MQTT CLIENT CLOSE - thinks it's done, successfully. ");
        ctx.succeed(buildResponse(sessionAttributes,
                buildSpeechletResponse(cardTitle, speechOutput, repromptText,
                    shouldEndSession)));
    }));

    client.on("error", (function (err, granted) {
        console.log("MQTT CLIENT ERROR!!  " + err);
    }));
}


// --------------- Helpers that build all of the responses -----------------------

function buildSpeechletResponse(title, output, repromptText, shouldEndSession) {
    return {
        outputSpeech: {
            type: "PlainText",
            text: output
        },
        card: {
            type: "Simple",
            title: title,
            content: output
        },
        reprompt: {
            outputSpeech: {
                type: "PlainText",
                text: repromptText
            }
        },
        shouldEndSession: shouldEndSession
    }
}

function buildResponse(sessionAttributes, speechletResponse) {
    return {
        version: "1.0",
        sessionAttributes: sessionAttributes,
        response: speechletResponse
    }
}
