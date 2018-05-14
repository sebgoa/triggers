#!/usr/bin/env python

import paho.mqtt.client as mqtt
import time

client = mqtt.Client()
client.connect("192.168.99.100", 31860, 60)
client.loop_start()

while True:
    time.sleep(2)
    client.publish("kubeless","wassup")
