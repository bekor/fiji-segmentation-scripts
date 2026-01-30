# Segmentation script for Fiji
There are two solution to run macro with Fiji

## Segmentation Macro in Fiji:
The segmentation.ijm file is an example macro for Fiji to do segmentation
Select the input folder of your images and select the output folder where the generated images will be saved
The macro contains NO error hadnling!

## Python script with Fiji:

The `./python-script` folder contains an example to run python script by using Fiji for segmentation.
The folder contains an environment file, and requirements.txt too
Segmentation file called `main.py`
Todo before running it:
- Python 3.12
- Have an installed Java (Fiji uses java the example code using a python wrapper package around it)
- Install requirements
- Set the following variables in the `.env` file:
-- `JAVA_HOME_PATH` to your java
-- `INPUT_DIR` folder for images you want to segment
-- `OUTPUT_DIR` segmented images
Script contains minimal error handling sorry...

Extracting some metric:
Run the `qualityControl.py`
This calculates IoU and Threshold for Unet predictions and Fiji segmented images
Todo before running it:
- Set the following `.env` variables:
-- `SOURCE_IMAGES` source images
-- `GROUND_TRUTH` ground truth images
-- `UNET_PREDICTION` U-Net predicted images
-- `FIJI_SEGMENTED` Fiji segmented images
- Install requirements (after you have a Python installation) 
