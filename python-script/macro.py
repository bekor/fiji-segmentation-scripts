macro = """
#@ String inputDirectory
#@ String outputDirectory
setBatchMode(true);
setBatchMode("hide");
segmentImages(inputDirectory+File.separator, outputDirectory+File.separator);

function segmentImages(inputDirectory, outputDirectory){
	imagesList = getFileList(inputDirectory);

	for(i = 0; i < imagesList.length; i++){
		currentImagePath = inputDirectory + imagesList[i];
		// Open image for segmentation
		open(currentImagePath);
		selectImage(imagesList[i]);
		shortName = File.nameWithoutExtension;
		// Do segmentation
		segment();
		// Save image
		outImageName = outputDirectory + shortName + "_p";
		saveAs("Png", outImageName);
		close("*");
	}
}

function segment() { 
	run("Duplicate...", "title=[10-cp.png]");
	setAutoThreshold("MaxEntropy dark");
	setOption("BlackBackground", true);
	run("Convert to Mask");
	
	run("Options...", "iterations=4 count=4 black edm=8-bit do=[Fill Holes]");
	run("Options...", "iterations=1 count=8 white edm=8-bit do=Erode");
	run("Options...", "iterations=2 count=4 white edm=8-bit do=Dilate");
	run("Options...", "iterations=2 count=3 white edm=8-bit do=Erode");
}
close("*");
"""