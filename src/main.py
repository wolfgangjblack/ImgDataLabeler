import os
import argparse
from utils import get_image_list, BoundingBoxAnnotator, boundingBoxExplainer, ClassifierAnnotator, classifierExplainer


def main(args):
    """
    Manual Image/Bounding Box Annotation Tool

    This script allows manual annotation of images with bounding boxes or classification labels.
    It takes command line arguments to specify the mode of annotation, the directory of images to process,
    the output directory to save the annotated data, the output file name, and the list of class names.

    Usage:
        python main.py [--mode MODE] [--image_dir IMAGE_DIR] [--output_dir OUTPUT_DIR]
                       [--output_file OUTPUT_FILE] [--classes CLASSES]

    Arguments:
        --mode (str): Mode of annotation (boundingBox or Classification). Default is 'boundingbox'.
        --image_dir (str): Directory of images to process. Default is './data/testimgs/'.
        --output_dir (str): Where to save output data. Default is './data/results/'.
        --output_file (str): Output file name. Default is 'annotations.json'.
        --classes (str): List of class names. Default is ['face'].

    """
   
    image_list = get_image_list(args.image_dir)
    output = os.path.join(args.output_dir, args.output_file)
    if args.mode == 'boundingbox':
        boundingBoxExplainer()
        annotator = BoundingBoxAnnotator(image_list, output, args.classes)
    elif args.mode == 'classifier':
        classifierExplainer()
        annotator = ClassifierAnnotator(image_list, output, args.classes)
    else:
        raise NotImplementedError("Invalid mode. Please choose either 'boundingbox' or 'classifier'.")
    annotator.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Manual Image/Bounding Box Annotation Tool')
    parser.add_argument('--mode', type=str, default='boundingbox', help='Mode of annotation (boundingBox or Classification)')
    parser.add_argument('--image_dir', type=str, default='./data/testimgs/', help='Directory of images to process')
    parser.add_argument('--output_dir', type=str, default='./data/results/', help='Where to save output data')
    parser.add_argument('--output_file', type=str, default='annotations.json', help='Output file name')
    parser.add_argument('--classes', type=str, nargs='+', default=['face'], help='List of class names')

    args = parser.parse_args()

    main(args)
