import os
from matplotlib.pyplot import imread
from pathlib import Path
from skimage import img_as_ubyte, io, transform
import numpy as np

def getIoUvsThreshold(prediction_filepath, groud_truth_filepath):
    prediction = io.imread(prediction_filepath)
    ground_truth_image = img_as_ubyte(io.imread(groud_truth_filepath, as_gray=True), force_copy=True)

    # calculate intersection over union
    IoU_score = 0
    treshold = 0
    for threshold in range(0,256):
        # Convert to 8-bit for calculating the IoU
        mask = img_as_ubyte(prediction, force_copy=True)
        mask[mask > threshold] = 255
        mask[mask <= threshold] = 0

        # Intersection over Union metric
        intersection = np.logical_and(ground_truth_image, np.squeeze(mask))
        union = np.logical_or(ground_truth_image, np.squeeze(mask))
        current_iou_score = np.sum(intersection) / np.sum(union)
                
        if current_iou_score > IoU_score:
            IoU_score = current_iou_score
            treshold = threshold
    return (treshold, IoU_score)