import os
from matplotlib import pyplot as plt
from matplotlib.pyplot import imread
from pathlib import Path
import csv
from skimage import img_as_ubyte, io, transform
import pandas as pd
import numpy as np
from dotenv import load_dotenv, dotenv_values 
load_dotenv()
from thresholdCalculator import getIoUvsThreshold

folderPath = {
    "sourceImages" : os.getenv("SOURCE_IMAGES"),
    "groundTruth" : os.getenv("GROUND_TRUTH"),
    "UNetPrediction" : os.getenv("UNET_PREDICTION"),
    "fijiSegmented" : os.getenv("FIJI_SEGMENTED"),
}

fileNameExtra = {
    "predictionPrefix" : "Predicted_",
    "fijiPostfix" : "_p"
}

#-----------------------------Calculate Metrics----------------------------------------#
QC_name = 'test'
QC_path = './QualityControl'
f = plt.figure(figsize=((5,5)))

def extractMetricsForImages(folderPath, fileNameExtra, QC_name, QC_path):
    filename_list = []
    uNet_threshold_list = []
    uNet_IoU_score_list = []
    fiji_IoU_score_list = []
    fiji_threshold_list = []
    
    with open(os.path.join(QC_path, 'QC_metrics_'+QC_name+'.csv'), "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["File name","IoU", "IoU-optimised threshold", "Fiji IoU", "Fiji optimised threshold"])

        # Initialise the lists

        for filename in os.listdir(folderPath["sourceImages"]):
            if not filename.endswith('.png') and not filename.endswith('.tif'):
                continue
            print(filename)
            source_path = os.path.join(folderPath["sourceImages"], filename)
            if not os.path.isdir(source_path):
                print('Running QC on: '+ filename)
                test_ground_truth_path = os.path.join(folderPath["groundTruth"], filename)
                prediction_file_name = fileNameExtra["predictionPrefix"]+os.path.splitext(filename)[0]+'.tif'
                fiji_file_name = os.path.splitext(filename)[0]+fileNameExtra["fijiPostfix"]+'.png'
                
                prediction_file_path = os.path.join(folderPath["UNetPrediction"], prediction_file_name)
                fiji_macro_file_path = os.path.join(folderPath["fijiSegmented"], fiji_file_name)
                
                test_input = io.imread(source_path, as_gray=True)
                test_ground_truth_image = io.imread(test_ground_truth_path, as_gray=True)
                (best_threshold, best_IoU_score) = getIoUvsThreshold(prediction_file_path, test_ground_truth_path)
                (best_threshold_fiji, best_IoU_score_fiji) = getIoUvsThreshold(fiji_macro_file_path, test_ground_truth_path)
                
                # Write the results in the CSV file
                writer.writerow([filename, str(best_IoU_score), str(best_threshold), str(best_IoU_score_fiji), str(best_threshold_fiji)])
                print(f'Unet, score: {best_IoU_score} thres: {best_threshold}, ff score: {best_IoU_score_fiji}, thres: {best_threshold_fiji}')
                # Here we append the best threshold and score to the lists
                filename_list.append(filename)
                uNet_IoU_score_list.append(best_IoU_score)
                uNet_threshold_list.append(best_threshold)
                fiji_IoU_score_list.append(best_IoU_score_fiji)
                fiji_threshold_list.append(best_threshold_fiji)
    return {
        "filename_list" : filename_list,
        "UNetData" : (uNet_IoU_score_list, uNet_threshold_list),
        "fijiData" : (fiji_IoU_score_list, fiji_threshold_list)
    }

def calculateResultTables(filename_list, UNetData, fijiData):
    # Table with metrics as dataframe output
    best_IoU_score_list = UNetData[0]
    best_threshold_list = UNetData[1]
    pdResults = pd.DataFrame(index = filename_list)
    pdResults["IoU"] = best_IoU_score_list
    pdResults["IoU-optimised threshold"] = best_threshold_list
    print(best_threshold_list)
    average_best_threshold = sum(best_threshold_list)/len(best_threshold_list)
    print(average_best_threshold)

    fiji_best_IoU_score_list = fijiData[0]
    fiji_best_threshold_list = fijiData[1]
    pdResultsFiji = pd.DataFrame(index = filename_list)
    pdResultsFiji["Fiji IoU"] = fiji_best_IoU_score_list
    pdResultsFiji["Fiji optimised threshold"] = fiji_best_threshold_list  
    average_fiji_best_threshold = sum(fiji_best_threshold_list)/len(fiji_best_threshold_list)
    return {
        "pdResults":pdResults, 
        "average_best_threshold": average_best_threshold, 
        "pdResultsFiji":pdResultsFiji, 
        "average_fiji_best_threshold":average_fiji_best_threshold}

# ------------- For display ------------
print('--------------------------------------------------------------')
def show_QC_results(pdMetric, folderPath, fileNameExtra, QC_path, file, fiji_file=None):

    if fiji_file is not None:
        plt.figure(figsize=(25,10))
        rows, cols = 2, 4
    else:
        plt.figure(figsize=(25,5))
        rows, cols = 1, 4

    #Input
    plt.subplot(rows,cols,1)
    plt.axis('off')
    plt.imshow(plt.imread(os.path.join(folderPath["sourceImages"], file)), aspect='equal', cmap='gray', interpolation='nearest')
    plt.title('Input')

    #Ground-truth
    plt.subplot(rows,cols,2)
    plt.axis('off')
    test_ground_truth_image = io.imread(os.path.join(folderPath["groundTruth"], file), as_gray=True)
    plt.imshow(test_ground_truth_image, aspect='equal', cmap='Greens')
    plt.title('Ground Truth')

    #Prediction
    average_best_threshold = pdMetric["average_best_threshold"]
    plt.subplot(rows,cols,3)
    plt.axis('off')
    test_path = os.path.join(folderPath["UNetPrediction"], fileNameExtra["predictionPrefix"]+os.path.splitext(file)[0]+'.tif')
    test_prediction = plt.imread(test_path)
    test_prediction_mask = np.empty_like(test_prediction)
    test_prediction_mask[test_prediction > average_best_threshold] = 255
    test_prediction_mask[test_prediction <= average_best_threshold] = 0
    plt.imshow(test_prediction, aspect='equal', cmap='Purples')
    plt.title('Prediction')

    #Overlay
    pdResults = pdMetric["pdResults"]
    plt.subplot(rows,cols,4)
    plt.axis('off')
    plt.imshow(test_ground_truth_image, cmap='Greens')
    plt.imshow(test_prediction_mask, alpha=0.5, cmap='Purples')
    metrics_title = 'Overlay (IoU: ' + str(round(pdResults.loc[file]["IoU"],3)) + ' T: ' + str(round(pdResults.loc[file]["IoU-optimised threshold"])) + ')'
    plt.title(metrics_title)

    if fiji_file is not None:
        file_path = os.path.join(folderPath["fijiSegmented"], fiji_file)
        # fiji results
        average_fiji_best_threshold = pdMetric["average_fiji_best_threshold"]
        plt.subplot(rows,cols,5)
        plt.axis('off')
        fiji_path = os.path.join(folderPath["fijiSegmented"], fiji_file)
        fiji_image = plt.imread(fiji_path)
        plt.imshow(fiji_image, aspect='equal', cmap='Purples')
        plt.title('Fiji Prediction')
        test_fiji_prediction_mask = np.empty_like(fiji_image)
        test_fiji_prediction_mask[fiji_image > average_fiji_best_threshold] = 255
        test_fiji_prediction_mask[fiji_image <= average_fiji_best_threshold] = 0

        # Overlay
        pdResultsFiji = pdMetric["pdResultsFiji"]
        plt.subplot(rows,cols,6)
        plt.axis('off')
        plt.imshow(test_ground_truth_image, cmap='Greens')
        plt.imshow(test_fiji_prediction_mask, alpha=0.5, cmap='Purples')
        fiji_metrics_title = 'Fiji Overlay (IoU: ' + str(round(pdResultsFiji.loc[file]["Fiji IoU"],3)) + ' T: ' + str(round(pdResultsFiji.loc[file]["Fiji optimised threshold"])) + ')'
        plt.title(fiji_metrics_title)
    
    plt.savefig(QC_path+'/QC_example_data.png',bbox_inches='tight',pad_inches=0)

if __name__ == "__main__":
    import pathlib
    # Create QualityControl folder if it does not exists
    pathlib.Path(QC_path).mkdir(exist_ok=True) 
    
    UNetAndFijimetrics = extractMetricsForImages(folderPath, fileNameExtra, QC_name, QC_path)
    
    results = calculateResultTables(
        UNetAndFijimetrics["filename_list"], 
        UNetAndFijimetrics["UNetData"], 
        UNetAndFijimetrics["fijiData"])
    
    print('--------------------------------------------------------------')
    print(f'Best average threshold is: {str(round(results["average_best_threshold"]))}')
    print('--------------------------------------------------------------')
    path_test_file = os.listdir(folderPath["sourceImages"])[2]
    fiji_test_file = os.path.splitext(path_test_file)[0]+fileNameExtra["fijiPostfix"]+'.png'

    show_QC_results(results, folderPath, fileNameExtra, QC_path, path_test_file, fiji_test_file)

