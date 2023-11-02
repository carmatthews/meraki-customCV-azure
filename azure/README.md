# Set up the bridge between the Meraki devices and Azure

## Prerequisites
1. You have successfully deployed the Azure IOT Hub and the device is registered.
2. At least 1 camera is configured in the Meraki dashboard

## Steps to Complete

1. Since IOT Hub has a specific requirement on the format of messages (devices/[device-id]/messages/events), we need a way to broker and translate messages sent from the Meraki devices into Azure.  To accomplish this, we will leverage Mosquitto.  Install Mosquitto Broker on your device.  If you are running the Debian Linux 11 (bullseye) you can follow these directions.  For other distributions you can search for the set up and verification steps.
    - [Mosquitto Installation Guide](https://www.howtoforge.com/how-to-install-mosquitto-mqtt-message-broker-on-debian-11/)

2. Once you have completed and verified your installation, you will need to add a certificate to your device.  For this sample, we will leverage the default public certificate for your IOT Hub and you can place it here /etc/mosquitto/ca_certificates/mosq.pem.  You can use the pem file located in the [mosquitto folder](mosquitto/mosq.pem).  You would never use a default certificate in a production environment, but for purposes of this repo you can use the generic certificate file.
    - For further reference: [Azure IOT Security](https://learn.microsoft.com/en-us/azure/iot/iot-overview-security)

3. Next, you need to create a bridge from mosquitto to azure and your IOY Hub.  This can be accomplished by adding bridge configuration to the mosquitto.conf file located here /etc/mosquitto/mosquitto.conf
```
# Bridge configuration
connection azureiot-bridge # this is the name you want to give your bridge
log_type all
address [hub fqdn]:8883
remote_username [iot hub name].azure-devices.net/[device-id]/?api-version=2021-04-12
remote_password [SharedAccessSignature]
remote_clientid [device-id]
bridge_cafile /etc/mosquitto/ca_certificates/mosq.pem # Use this location if this is where you placed the cert file
try_private false
cleansession true
start_type automatic
bridge_insecure false
bridge_protocol_version mqttv311
notifications false

topic devices/[device-id]/messages/events/# out 1
```

- Replace the following:
    - **[hub fqdn]** the IOT Hub DNS name you created in step 1.  This includes .azure-devices.net
    - **[iot hub name]** the IOT Hub name you created in step 1.
    - **[device-id]** the name of the IOT device you set up in step 1.
    - **[SharedAccessSignature]**  You will need to generate one and replace when the SAS token has expired.  You can generate this using the Cloud Shell in your Azure portal
    ```
    az iot hub generate-sas-token -d [device-id] -n [iot hub name] --du 360000
    ```
    - After executing the command, copy the entire quoted string as your **[SharedAccessSignature]**
- The last line in the bridge configuration subscribes this bridge to all messages that are sent with that topic structure.  Remember to replace **[device-id]** in this line as well.
- Restart your mosquitto broker.  You should see debug messages that it is connected to your IOT Hub
- If you want to test the connection, you can send a test message
    ```
    mosquitto_pub -t devices/[device-id]/messages/events/ -m "Testing 123"
    ```

4. Since we cannot change the topic structure on the Meraki devices we must use some code to listen to messages, change the format for some additional information, and then send the message with the re-formatted topic structure.  Use the [helper.py](mosquitto/helper.py) as the baseline for these changes.  Please this file somewhere convenients within /etc/mosquitto.
- You will need to change the following:
    - Replace the **[device-id]** in the topic structure with the name of your device
    ```
    iothubmqtttopic = "[device-id]"
    ```
    - On line 34 starts the part of the code where you will translate the device mapped in the Meraki dashboard to the messages.  This will enable you to decipher which device sent the message.  In this sample code, there are 2 devices.  The temperature sensor which is an MV10 and a camera which is an MV63.  You must at least have a camera.  The value in the topic is the MAC address of the sensor, replace [sensorMacAddressx] with your corresponding MAC address.  Set the sensor name to what you named your sensor in the Meraki Dashboard (or whatever you want)
    ```
    if(topicStr.__contains__("[sensorMacAddress1]")):
        sensorName = "tempHumid1"
    elif(topicStr.__contains__("[sensorMacAddress2]")):
        sensorName = "camera1"
    ```
    - The next change will be for the messages containing your vision model results.  [cameraSerialNumber] is the serial number of your camera.  Replace [cameraSerialNumber] with your camera serial number.  Set the sensor name to something that indicates the message has the custom model.  In this sample, we used cameraCV.
    ```
         elif(topicStr.__contains__("[cameraSerialNumber]")):
               sensorName = "cameraCV"
    ```
    - The last change is to replace broker address with the FQDN or IP address of your MQTT broker.  In this case we are using a local mosquitto broker
    ```
        broker_address="localhost"
    ```

5. Get the IP address of your device that is acting as your broker.  You will need this for the next step.  You can use the following command to get the IP address
    ```
    hostname -I
    ```

6. Now we need to connect the Meraki devices to our broker devices.  You can find the instructions for how to do this in the Meraki documentation. [MQTT Data Streaming](https://documentation.meraki.com/MR/Other_Topics/MR_MQTT_Data_Streaming)

7. The very last step is to put everything together.  Go to the location where you have puter the hilper.py file.  Begin execution of the file
```
    python helper.py
```
If you left the print statements in the Python file, you should see messages coming through.  You can also verify that the messages are being sent to your IOT Hub by going to the IOT Hub in the Azure portal and selecting the **Message Routing** option.  You should see the messages being sent to the IOT Hub.

## Troubleshooting
- If you are not seeing messages in your IOT Hub, you can check the logs on your device to see if there are any errors.  You can use the following command to see the logs
```
    mosquitto_sub -v -t devices/[device-id]/messages/events/#
```
You can also check the logs
```
    tail -f /var/log/mosquitto/mosquitto.log
```