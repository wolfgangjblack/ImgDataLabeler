import os
import cv2
import json
import random
import numpy as np
from tqdm import tqdm

def get_image_list(image_dir):
    image_list = []
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            if file.endswith('.jpg') or file.endswith('.png') or file.endswith('.jpeg'):
                image_list.append(os.path.join(root, file))
    random.shuffle(image_list)
    return image_list

class BoundingBoxAnnotator:
    def __init__(self, image_files, output_file, classes):
        self.output_file = output_file
        self.annotations = []
        self.image_files = image_files
        self.current_image_index = 0
        self.drawing = False
        self.ix, self.iy = -1, -1
        self.bboxes = []
        self.classes = classes
        self.current_class_index = 0
        self.current_class = classes[0]

        cv2.namedWindow('Image')
        cv2.setMouseCallback('Image', self.draw_bbox)

    def draw_bbox(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.ix, self.iy = x, y

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                img = self.current_image.copy()
                cv2.rectangle(img, (self.ix, self.iy), (x, y), (0, 255, 0), 2)
                img_with_info = self.display_info(img)
                cv2.imshow('Image', img_with_info)

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            bbox = [self.current_class, self.ix, self.iy, x, y]
            self.bboxes.append(bbox)
            cv2.rectangle(self.current_image, (self.ix, self.iy), (x, y), (0, 255, 0), 2)
            img_with_info = self.display_info(self.current_image)
            cv2.imshow('Image', img_with_info)

    def save_annotations(self):
        if self.bboxes:
            annotation = {
                'image': self.image_files[self.current_image_index],
                'bboxes': self.bboxes
            }
            self.annotations.append(annotation)
            self.bboxes = []

    def display_info(self, img):
        img_height, img_width = img.shape[:2]
        info_height = 50  # Height of the information area below the image
        text_image = 255 * np.ones((img_height + info_height, img_width, 3), np.uint8)
        text_image[:img_height, :] = img

        image_name = os.path.basename(self.image_files[self.current_image_index])
        cv2.putText(text_image, image_name, (10, img_height + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        class_info = f"current bb class: {self.current_class}, class {self.current_class_index + 1}/{len(self.classes)}"
        cv2.putText(text_image, class_info, (10, img_height + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        return text_image

    def run(self):
        with tqdm(total=len(self.image_files), desc="Annotating images") as pbar:
            while self.current_image_index < len(self.image_files):
                image_path = self.image_files[self.current_image_index]
                self.current_image = cv2.imread(image_path)
                img_with_name = self.display_info(self.current_image)
                cv2.imshow('Image', img_with_name)
                key = cv2.waitKey(0)

                if key == ord('n'):
                    self.save_annotations()
                    self.current_image_index += 1
                    self.current_class_index = 0
                    if self.current_image_index < len(self.image_files):
                        self.current_class = self.classes[self.current_class_index]
                    pbar.update(1)
                elif key == ord('q'):
                    break
                elif key == ord('x'):  # Clear all bboxes for the current image
                    self.bboxes = []
                    self.current_class_index = 0
                    self.current_class = self.classes[self.current_class_index]
                    self.current_image = cv2.imread(image_path)
                    img_with_name = self.display_info(self.current_image)
                    cv2.imshow('Image', img_with_name)
                elif key == ord('c'):  # Clear all bboxes for the current class
                    self.bboxes = [bbox for bbox in self.bboxes if bbox[0] != self.current_class]
                    self.current_image = cv2.imread(image_path)
                    for bbox in self.bboxes:
                        cv2.rectangle(self.current_image, (bbox[1], bbox[2]), (bbox[3], bbox[4]), (0, 255, 0), 2)
                    img_with_name = self.display_info(self.current_image)
                    cv2.imshow('Image', img_with_name)
                elif key == ord('s'):  # Change class label
                    if self.current_class_index == len(self.classes) - 1:
                        self.save_annotations()
                        self.current_image_index += 1
                        self.current_class_index = 0
                        if self.current_image_index < len(self.image_files):
                            self.current_class = self.classes[self.current_class_index]
                        pbar.update(1)
                    else:
                        self.current_class_index = (self.current_class_index + 1) % len(self.classes)
                        self.current_class = self.classes[self.current_class_index]
                    if self.current_image_index < len(self.image_files):
                        img_with_name = self.display_info(self.current_image)
                        cv2.imshow('Image', img_with_name)

        self.save_annotations_to_file()
        cv2.destroyAllWindows()

    def save_annotations_to_file(self):
        with open(self.output_file, 'w') as f:
            json.dump(self.annotations, f, indent=4)


def boundingBoxExplainer():
    explanation = """
The script is running in bounding box mode. This mode allows you to draw bounding boxes around objects in images based on the supplied classes
    Instructions:
        Press 'n' to move to the next image 
            - do this if you are done annotating the current image
        Press 'q' to quit the annotation process 
            - this will save the annotations and exit the script
        Press 'x' to clear all bounding boxes for the current image 
            - do this if you want to start over on the current image
        Press 'c' to clear all bounding boxes for the current image on the current class
            - do this if you want to accidently have extranous labels for the current class
        Press 's' to annotate bounding boxes for the next class
            - Do this to step through classes per image
            - If at last class, this will move to the next image
    """
    print(explanation)
    return
