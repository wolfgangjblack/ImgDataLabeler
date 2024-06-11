# ImgDataLabeler
This repo contains scripts for downloading image data from CivitAI based on tags and prompts, and then a script to manual label the images either with bounding boxes or labels for detection and classification

## Usage:

This section contains information on how to use this repo. 

### preDataCapture

This folder contains the files necessary to run the data capture from the civitai postgres database and the code to download images from that dataset locally for labeling.

1. run `python -m venv venv` to set up a local virtual env
2. then to get dependencies activate the venv and run `pip install requirements.txt`
3. run `getData.ipynb` changing the query as necessary
4. run `downloadData.ipynb` to save files locally

After this we're ready to run `main.py` in `src`

### Datalabeler

`python main.py [--mode MODE] [--image_dir IMAGE_DIR] [--output_dir OUTPUT_DIR] [--output_file OUTPUT_FILE] [--classes CLASSES]`

Arguments:
- --mode (str): Mode of annotation (boundingBox or Classification). Default is 'boundingbox'.
- --image_dir (str): Directory of images to process. Default is './data/testimgs/'.
- --output_dir (str): Where to save output data. Default is './data/results/'.
- --output_file (str): Output file name. Default is 'annotations.json'.
- --classes (str): List of class names. Default is ['face'].

#### --mode boundingbox

This mode allows you to draw bounding boxes around objects in images based on the supplied classes
##### Instructions:
- Press 'n' to move to the next image 
    - do this if you are done annotating the current image
- Press 'q' to quit the annotation process 
    - this will save the annotations and exit the script
- Press 'x' to clear all bounding boxes for the current image 
    - do this if you want to start over on the current image
- Press 'c' to clear all bounding boxes for the current image on the current class
    - do this if you want to accidently have extranous labels for the current class
- Press 's' to annotate bounding boxes for the next class
    - Do this to step through classes per image
    - If at last class, this will move to the next image

#### --mode classifier
This mode allows the user to provide classes to the datalabeler to label single class classifications. The classes become buttons below the image, which the user can click to label the image. Right now only single image classification is supported. 

##### Instructions:
- When calling the script, make sure to set mode to `classifier` and include the classes you want to label. 
- Look at the image and determine which of the provided class buttons best represent the image.
    - to select those classes, click the buttons
- Press 'n' to move to the next image 
    - do this once you've clicked on the class corresponding to the current image
    - if you click 'n' without selecting a class, the image will be skipped
- Press 'c' to clear all selected classes for the current image
- Press 'q' to quit the annotation process 
    - this will save the annotations and exit the script
    - note: if you have selected classes and hit 'q' before hitting 'n', the labels will not be saved to the output json