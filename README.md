# Custom Computer Vision on Azure for Meraki MV Camera

This tutorial guides you through the process of Capturing images, prepare a labeled dataset, train a custom object detection model and deploy to Meraki MV camera using Azure Machine Learning and Python.  

Then you can analyze data from the device and the results of object model by streaming to the cloud using Azure IoT Hub, Azure Data Explorer, and PowerBI visualizations.

![Meraki on Azure Architecture](images/Meraki_Auzre_Arch.png)

# Prerequisites

1. Cisco Meraki MV 2nd Generation Camera (MV2, MV12, MV32, MV22, MV72)
2. Software version 4.18 on the camera
3. Microsoft Azure Subscription

# Steps to Complete

1. [Image Capture](#image_capture).  Use the Meraki MV Camera to capture images to use for training a custom object detection model.
2. Use the Azure Machine Learning labeling project to prepare the data.
3. Train an object detection model using Azure Machine Learning Notebooks.
4. Deploy the model to the Meraki MV Camera.
5. Setup Streaming to Azure
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

When you're ready and you have positioned the camera and objects you wish to use in the desired location and position, you can run the script with ```python cvSnapper.py```.

The script will do the following:

1. It will create a directory structure in the form:

```
images/
|_train/
|_test/
```

2. It will prompt you with ```Press Enter to capture snapshot:```, and after you press Enter (with no other input), it will generate a Snapshot from the camera you chose. It can be useful to have a Meraki Dashboard video stream of the camera open side by side to know what the camera is looking at before you request the snapshot and make any necessary adjustments.

3. It will then ask you if you want to ```Keep image? (Y/N):``` . If you answer ```Y``` it will increase the snap counter, and save the image as ```snap_{snap_count}.jpg``` in the images folder.
4. If you answer ```N```, it will discard the image and ask you if you wish to continue or not. If you answer ```Y```, it will prompt you again to take a new snapshot, and if you answer ```N``` it will exit the program
5. The script will continue fetching snapshots until the counter reaches your ```desired_snaps``` setting, and you have the desired number of images.
6. After this, the script will randomly split your captured images according to your specified ```train_test_split``` and will place them in the ```train``` and ```test``` folders.