import paho.mqtt.client as mqtt
import time
import json

#replace [device-id] with your device you created in IoT Hub.
iothubmqtttopic = "[device-id]"

# remove print statements if you don't care to see message transformations

# this code resends the incoming message (on any topic) and just
# resends it on the iothub topic structure.  you could, of course, do any
# kind of sophisticated processing here you wanted...
def on_message(client, userdata, message):
     global iothubmqtttopic
     if(message.topic != iothubmqtttopic):
         # Extract the topic and message from the received message
         messageStr = str(message.payload.decode("utf-8"))
         messageData = json.loads(messageStr)
         print("message as json=", messageData)
         topicStr = message.topic
         # Extract the sensor reading from the topic
         sesnorReading = topicStr.split("/")[-1]
         newData1 = {"sensorReading": sesnorReading}
         messageData.update(newData1)
         print("New Data=", messageData)
         print("sensor reading=", sesnorReading)
         sensorName = "unknown"

         # Determine the sensor name based on the topic
         # This is a bit of a hack, but it works for demo purposes
         # The value in the topic is the MAC address of the sensor, replace [sensorMacAddress1..x] with your corresponding MAC address
         # The MAC Address has colons in it
         # Set the sensor name to what you named your sensor in the Meraki Dashboard (or whatever you want)
         # In this example, I have a temperature/humidity sensor and a camera.  You must at least have 1 camera
         if(topicStr.__contains__("[sensorMacAddress1]")):
               sensorName = "tempHumid1"
         elif(topicStr.__contains__("[sensorMacAddress2]")):
               sensorName = "camera1"
         # >>> NOTE <<<
         # >>> This should be the serial number for the camera containing the deployed model 
         # >>> The serial number has dashes in it
         # >>> Change Below <<<
         elif(topicStr.__contains__("[cameraSerialNumber]")):
               sensorName = "cameraCV"

         print("sensorName= " ,sensorName)
         newData2 = {"sensorName": sensorName}
         messageData.update(newData2)
         print("New Data=", messageData)
         print("message received " ,messageStr)
         print("message topic=",message.topic)
         client.publish(iothubmqtttopic, json.dumps(messageData))

# replace broker address with the FQDN or IP address of your MQTT broker
# In this case we are using a local mosquitto broker
broker_address="localhost"

print("creating new instance")
client = mqtt.Client("iottopicxlate") #create new instance
client.on_message=on_message #attach function to callback
print("connecting to broker")
client.connect(broker_address) #connect to broker

print("Subscribing to all topics")
client.subscribe("#")

client.loop_forever() #stop the loop
