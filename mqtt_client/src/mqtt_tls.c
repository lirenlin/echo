/* Copyright Statement:
 *
 * (C) 2005-2016  MediaTek Inc. All rights reserved.
 *
 * This software/firmware and related documentation ("MediaTek Software") are
 * protected under relevant copyright laws. The information contained herein
 * is confidential and proprietary to MediaTek Inc. ("MediaTek") and/or its licensors.
 * Without the prior written permission of MediaTek and/or its licensors,
 * any reproduction, modification, use or disclosure of MediaTek Software,
 * and information contained herein, in whole or in part, shall be strictly prohibited.
 * You may only use, reproduce, modify, or distribute (as applicable) MediaTek Software
 * if you have agreed to and been bound by the applicable license agreement with
 * MediaTek ("License Agreement") and been granted explicit permission to do so within
 * the License Agreement ("Permitted User").  If you are not a Permitted User,
 * please cease any access or use of MediaTek Software immediately.
 * BY OPENING THIS FILE, RECEIVER HEREBY UNEQUIVOCALLY ACKNOWLEDGES AND AGREES
 * THAT MEDIATEK SOFTWARE RECEIVED FROM MEDIATEK AND/OR ITS REPRESENTATIVES
 * ARE PROVIDED TO RECEIVER ON AN "AS-IS" BASIS ONLY. MEDIATEK EXPRESSLY DISCLAIMS ANY AND ALL
 * WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE OR NONINFRINGEMENT.
 * NEITHER DOES MEDIATEK PROVIDE ANY WARRANTY WHATSOEVER WITH RESPECT TO THE
 * SOFTWARE OF ANY THIRD PARTY WHICH MAY BE USED BY, INCORPORATED IN, OR
 * SUPPLIED WITH MEDIATEK SOFTWARE, AND RECEIVER AGREES TO LOOK ONLY TO SUCH
 * THIRD PARTY FOR ANY WARRANTY CLAIM RELATING THERETO. RECEIVER EXPRESSLY ACKNOWLEDGES
 * THAT IT IS RECEIVER'S SOLE RESPONSIBILITY TO OBTAIN FROM ANY THIRD PARTY ALL PROPER LICENSES
 * CONTAINED IN MEDIATEK SOFTWARE. MEDIATEK SHALL ALSO NOT BE RESPONSIBLE FOR ANY MEDIATEK
 * SOFTWARE RELEASES MADE TO RECEIVER'S SPECIFICATION OR TO CONFORM TO A PARTICULAR
 * STANDARD OR OPEN FORUM. RECEIVER'S SOLE AND EXCLUSIVE REMEDY AND MEDIATEK'S ENTIRE AND
 * CUMULATIVE LIABILITY WITH RESPECT TO MEDIATEK SOFTWARE RELEASED HEREUNDER WILL BE,
 * AT MEDIATEK'S OPTION, TO REVISE OR REPLACE MEDIATEK SOFTWARE AT ISSUE,
 * OR REFUND ANY SOFTWARE LICENSE FEES OR SERVICE CHARGE PAID BY RECEIVER TO
 * MEDIATEK FOR SUCH MEDIATEK SOFTWARE AT ISSUE.
 */

/* Includes ------------------------------------------------------------------*/
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "FreeRTOS.h"
#include "task.h"
#include "wifi_api.h"

#include "MQTTClient.h"
#include "mqtt.h"
#include "syslog.h"
#include "aws_iot.h"
#include "cJSON.h"
#include "hal.h"

#ifdef MQTT_USR_TLS
static const char mqtt_ca_cert[] = AWS_MQTT_CA_CRT;
static const size_t mqtt_ca_crt_len  = sizeof( mqtt_ca_cert );
extern hal_gpio_pin_t led_pins[];

#define MQTT_SERVER	"avkhjfj8t3ivk.iot.eu-west-1.amazonaws.com"
#define MQTT_TOPIC 	"$aws/things/dummy/shadow/update"
#define MQTT_PORT	"8883"
#define MQTT_CLIENT_ID	"mqtt-7687-client-ssl"
#define MQTT_MSG_VER	"0.50"

static int arrivedcount = 0;
static int stop = 0;

log_create_module(mqtt_tls, PRINT_LEVEL_INFO);

static void callBack (char *intent, char *argument, int num)
{
	if (strcmp (intent, "SetLightStatus") == 0)
	{
		int i;
		for (i = 0; i < 4; ++i)
		{
			if (num != 4 && i != num)
				continue;

			hal_gpio_pin_t pin = led_pins[i];
			if (strcmp (argument, "off") == 0)
				hal_gpio_set_output (pin, HAL_GPIO_DATA_LOW);
			else if (strcmp (argument, "on") == 0)
				hal_gpio_set_output (pin, HAL_GPIO_DATA_HIGH);
			else
				LOG_I (mqtt_tls, "Unknow intent value");


		}

	}
	else
		LOG_I (mqtt_tls, "Unknow intent");
}

/**
* @brief          MQTT message RX handle
* @param[in]      MQTT received message data
* @return         None
*/
static void messageArrived(MessageData *md)
{
    MQTTMessage *message = md->message;
    char *payload = (char *)(message->payload);
    cJSON *json;

    char *intent;
    char *argument;
    int num = 0;

    //LOG_I(mqtt_tls, "Message arrived: qos %d, retained %d, dup %d, packetid %d\n", 
    //    message->qos, message->retained, message->dup, message->id);
    LOG_I(mqtt_tls, "Payload %d.%s\n", (size_t)(message->payloadlen), payload);

    json = cJSON_Parse (payload);
    if (!json) {
	LOG_I (mqtt_tls, "Error parsing mqtt message");
	return;
    } else {
	    cJSON *item = cJSON_GetObjectItem (json, "name");
	    intent = item->valuestring;
	    if (strcmp (intent, "SetLightStatus") == 0)
	    {
		    cJSON *item = cJSON_GetObjectItem (json, "status");
			  if (item)
				  argument = item->valuestring;
				
				item = cJSON_GetObjectItem (json, "num");
				if (item)
				  num = item->valueint - 1;

				LOG_I (mqtt_tls, "%s, %s, %d", intent, argument, num);
				callBack (intent, argument, num);
		  }
			else if (strcmp (intent, "stop") == 0)
				stop = 1; 
    }
    ++arrivedcount;
}

/**
* @brief          MQTT client example entry function
* @return         None
*/
extern int mqtt_client_example_ssl(void)
{
    int rc = 0;
    unsigned char msg_buf[100];     //Buffer for outgoing messages, such as unsubscribe.
    unsigned char msg_readbuf[100]; //Buffer for incoming messages, such as unsubscribe ACK.

    Network n;  //TCP network
    Client c;   //MQTT client
    MQTTPacket_connectData data = MQTTPacket_connectData_initializer;
    char *topic = MQTT_TOPIC;
    
#ifdef MQTT_USE_CLIENT_CERT
    const char mqtt_cli_cert[] = AWS_MQTT_CLI_CRT;
    const char mqtt_cli_key[] = AWS_MQTT_CLI_KEY;
    const size_t mqtt_cli_crt_len  = sizeof( mqtt_cli_cert );
    const size_t mqtt_cli_key_len  = sizeof( mqtt_cli_key );
#endif

    //Initialize MQTTnetwork structure
    NewNetwork(&n);

    //Connect to remote server
    LOG_I(mqtt_tls, "TLS Connect to %s:%s\n", MQTT_SERVER, MQTT_PORT);
    rc = TLSConnectNetwork(&n, MQTT_SERVER, MQTT_PORT, mqtt_ca_cert, mqtt_ca_crt_len,
#ifdef MQTT_USE_CLIENT_CERT
    		mqtt_cli_cert, mqtt_cli_crt_len,
    		mqtt_cli_key, mqtt_cli_key_len,
    		NULL, 0);
#else
    		NULL, 0, NULL, 0, NULL, 0);
#endif

    if (rc != 0) {
        LOG_I(mqtt_tls, "TCP connect fail,status -%4X\n", -rc);
        return rc;
    }

    //Initialize MQTT client structure
    MQTTClient(&c, &n, 12000, msg_buf, 100, msg_readbuf, 100);

    //The packet header of MQTT connection request
    data.willFlag = 0;
    data.MQTTVersion = 3;
    data.clientID.cstring = MQTT_CLIENT_ID;
    data.username.cstring = NULL;
    data.password.cstring = NULL;
    data.keepAliveInterval = 1000;
    data.cleansession = 1;

    //Send MQTT connection request to the remote MQTT server
    rc = MQTTConnect(&c, &data);

    if (rc != 0) {
        LOG_I(mqtt_tls, "MQTT connect failed,status -%4X\n", -rc);
        return rc;
    }

    LOG_I(mqtt_tls, "Subscribing to %s\n", topic);
    rc = MQTTSubscribe(&c, topic, QOS1, messageArrived);
    LOG_I(mqtt_tls, "Client Subscribed %d\n", rc);

    while (stop == 0) {
        MQTTYield(&c, 1000);
    }

    if ((rc = MQTTUnsubscribe(&c, topic)) != 0) {
        LOG_I(mqtt_tls, "The return from unsubscribe was %d\n", rc);
    }
    LOG_I(mqtt_tls, "MQTT unsubscribe done\n");

    if ((rc = MQTTDisconnect(&c)) != 0) {
        LOG_I(mqtt_tls, "The return from disconnect was %d\n", rc);
    }
    LOG_I(mqtt_tls, "MQTT disconnect done\n");

    n.disconnect(&n);
    LOG_I(mqtt_tls, "Network disconnect done\n");
    LOG_I(mqtt_tls, "example project test success.");

    return 0;
}
#endif
