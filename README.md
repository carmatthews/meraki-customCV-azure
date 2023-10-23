# Custom Computer Vision on Azure for Meraki MV Camera

This tutorial guides you through the process of capturing images, labeling a dataset, training a custom object detection model and deploying to a Meraki MV camera using Azure Machine Learning and Python.  

You can also analyze data from the device and the results of custom object detection model by streaming to the cloud using Azure IoT Hub, Microsoft Fabric Eventstream, Azure KQL Database, and PowerBI visualizations.

![Meraki on Azure Architecture](images/Meraki_Auzre_Arch.png)

# Prerequisites

1. Cisco Meraki MV 2nd Generation Camera (MV2, MV12, MV32, MV22, MV72)
2. Software version 4.18 on the camera
3. Microsoft Azure Subscription
4. An micro computer of a Linux distribution.  This demo used a raspberry PI 4 device running the bullseye respberry pi os 

# Steps to Complete

**Step 1.** [Image Capture](#image_capture).  Use the Meraki MV Camera to capture images to use for training a custom object detection model.

**Step 2.** [Labeling](#labeling). Use the Azure Machine Learning labeling project to prepare the data.

3. Train an object detection model using Azure Machine Learning Notebooks.
4. Deploy the model to the Meraki MV Camera.

**Step 5.** [Azure](#azure). Setup Streaming to Azure.

6. Analyze.

<a name="image_capture"></a>

# Step 1: Image Capture

The first step is to capture a set of images to use for training a custom object detection model.  

## Tips for Image Capture
*   Capture enough images to include a minimum of 50 examples of each class to be detetcted - but the more the better.  

* Keep the ratio between the most and least frequently captured classes below 2 to 1.

* The more classes you have, the more individaul samples per class you will need.  If you have more than 50 classes, you would want a minimum of 200 examples of each class.

* It's helpful to capture images with different lighting, settings, and combinations that are relevant to the scenario the model would be used in.

* Place the objects in different orientations, positions, locations, and include some objects that you do NOT want to detect as well.  Also, you may want to partially obscure some of the objects as well, by blocking with other objects or not being in completley in the frame.

For more information and suggestion see: [Improve your Custom Vision Model](https://learn.microsoft.com/en-us/azure/ai-services/custom-vision-service/getting-started-improving-your-classifier).

## Using the Meraki Camera

The [cvSnapper.py](image_capture/cvSnapper.py) script uses a Meraki camera to take snapshots of objects within the frame. 

First, set the following values In the [config.py](image_capture/config.py) file:

1. `api_key` is your Meraki Dashboard API Key. If you don't know how to generate one, follow the instructions in this [article](https://documentation.meraki.com/General_Administration/Other_Topics/Cisco_Meraki_Dashboard_API).

2. `camera_serial` is the serial number of the camera you will be working with.

3. `desired_snaps` is the number of snapshots you wish to take to construct your dataset. The more the better, especially if you want to be able to recognize many different classes, but you should see decent accuracy with around 100 images and 4 classes total.

4. `dataset_name` is how you want to name your dataset.  For example, `meraki_images`.

5. `train_test_split` is the percentage of images in the dataset that will be used for training, while the remaining ones will be used for testing.

Once you have completed setting up the `config.py`, the next steps setup the envrionment and snapshot script. 

1.  In line `12` of the `cvSnapper.py` script, change the `win_or_mac` variable to `mac` or `win` depending on your environment.

2. Run `pip install -r requirements.txt` to install the required Python libraries before proceeding (in the image_capture directory of this repo).

When you're ready and you have positioned the camera and objects you wish to use in the desired location and position, you can run the script with `python cvSnapper.py`.

The script will do the following:

1. It will create a directory structure in the form:

```
images/
|_train/
|_test/
```

2. It will prompt you with `Press Enter to capture snapshot:`, and after you press Enter (with no other input), it will generate a Snapshot from the camera you chose. It can be useful to have a Meraki Dashboard video stream of the camera open side by side to know what the camera is looking at before you request the snapshot and make any necessary adjustments.

3. It will then ask you if you want to `Keep image? (Y/N):` . If you answer `Y` it will increase the snap counter, and save the image as `snap_{snap_count}.jpg` in the images folder.
4. If you answer `N`, it will discard the image and ask you if you wish to continue or not. If you answer `Y`, it will prompt you again to take a new snapshot, and if you answer `N` it will exit the program
5. The script will continue fetching snapshots until the counter reaches your `desired_snaps` setting, and you have the desired number of images.
6. After this, the script will randomly split your captured images according to your specified `train_test_split` and will place them in the `train` and `test` folders.

<a name="labeling"></a>

# Step 2: Labeling

Once you have captured the images, use the **Azure Machine Learning Labeling Project** to prepare the dataset for training.   

For general information about this service please see [Image labeling capabilities](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-create-image-labeling-projects?view=azureml-api-2#image-labeling-capabilities.
).

Detailed instructions for this tutorial are [here](labeling/README.md).

<a name="azure"></a>

# Step 5: Setup Streaming to Azure

1. The device Run the following to deploy the Azure resources needed for IOT and streaming
### ADD CODE HERE ###

2. Since IOT Hub has a specific requirement on the format of messages (devices/[device-id]/messages/events), we need a way to broker and translate messages sent from the Meraki devices into Azure.  To accomplish this, we will leverage Mosquitto.  Install Mosquitto Broker on your device.  If you are running the Debian Linux 11 (bullseye) you can follow these directions.  For other distributions you can search for the set up and verification steps.
    - [Mosquitto Installation Guide](https://www.howtoforge.com/how-to-install-mosquitto-mqtt-message-broker-on-debian-11/)

3. Once you have completed and verified your installation, you will need to add a certifcate to your device.  For this sample, we will leverage the default public certificate for your IOT Hub and you can place it here /etc/mosquitto/ca_certificates/mosq.pem.  You can use the pem file located in the [mosquitto folder](/mosquitto/).  You would never use a default certificate in a production environment, but for purposes of this repo you can use the generic certificate file.
    - For further reference: [Azure IOT Security](https://learn.microsoft.com/en-us/azure/iot/iot-overview-security)

4. Next, you need to create a bridge from mosquitto to azure and your IOY Hub.  This can be accomplished by adding bridge configuration to the mosquitto.conf file located here /etc/mosquitto/mosquitto.conf
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

5. Since we cannot change the topic structure on the Meraki devices we must use some code to listen to messages, change the format for some additional information, and then send the message with the re-formatted topic structure.  Use the [helper.py](/mosquitto/helper.py) as the baseline for these changes.  
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
    - The next change will be for the messages containing your vision model results.  [cameraSerialNumber] is the serial number of your camera.  Replace [cameraSerialNumber] with your camera serial number.  Set the sensor name to what you named your sensor in the Meraki Dashboard (or whatever you want)
    ```

