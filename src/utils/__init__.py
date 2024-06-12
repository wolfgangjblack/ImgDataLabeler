import os
import cv2
import json
import random
import numpy as np
import tkinter as tk
from tqdm import tqdm
from tkinter import ttk
from PIL import Image, ImageTk

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

        self.root = tk.Tk()
        self.root.withdraw()

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Calc the image display
        self.image_width = int(min(self.screen_width * 0.5, 600))
        self.image_height = int(min(self.screen_height * 0.5, 600))

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
        if os.path.isdir(os.path.dirname(self.output_file)) == False:
            os.makedirs(os.path.dirname(self.output_file))

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


class ClassifierAnnotator:
    def __init__(self, image_files, output_file, classes):
        self.output_file = output_file
        self.annotations = []
        self.image_files = image_files
        self.current_image_index = 0
        self.classes = classes
        self.selected_classes = []

        self.root = tk.Tk()
        self.root.title("Classifier Annotator")

        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Get a new resize value based on screen dimensions
        self.image_width = int(min(self.screen_width * 0.5, 600))
        self.image_height = int(min(self.screen_height * 0.5, 600))
        self.text_size = 50


        self.canvas = tk.Canvas(self.root, width=self.image_width, height=self.image_height+self.text_size)  # Fixed size canvas
        self.canvas.pack()

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack()


        self.buttons = []
        for cls in classes:
            btn = tk.Button(self.button_frame, text=cls, command=lambda c=cls: self.select_class(c))
            btn.pack(side=tk.LEFT)
            self.buttons.append(btn)

        self.info_label = tk.Label(self.root, text="")
        self.info_label.pack()

        self.root.bind('<n>', self.next_image)
        self.root.bind('<c>', self.clear_classes)
        self.root.bind('<q>', self.quit)

        self.update_image()

    def select_class(self, class_name):
        if class_name not in self.selected_classes:
            self.selected_classes.append(class_name)
        self.update_info_label()

    def update_image(self):
        image_path = self.image_files[self.current_image_index]
        img = Image.open(image_path)
        img.thumbnail((self.image_width, self.image_height))
        
        # Resizing the image
        canvas_image = Image.new("RGB", (self.image_width, self.image_height), (255, 255, 255))
        img_width, img_height = img.size
        offset = ((self.image_width - img_width) // 2, (self.image_height - img_height) // 2)
        canvas_image.paste(img, offset)
        
        self.img_tk = ImageTk.PhotoImage(canvas_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img_tk)
        self.update_info_label()

    def update_info_label(self):
        image_name = os.path.basename(self.image_files[self.current_image_index])
        selected_classes_str = ", ".join(self.selected_classes)
        self.info_label.config(text=f"Image: {image_name}\nSelected classes: {selected_classes_str}\nIf okay, hit 'n'")

    def save_annotations(self):
        if self.selected_classes:
            annotation = {
                'image': self.image_files[self.current_image_index],
                'classes': self.selected_classes
            }
            self.annotations.append(annotation)
        self.selected_classes = []

    def next_image(self, event=None):
        self.save_annotations()
        self.current_image_index += 1
        if self.current_image_index < len(self.image_files):
            self.update_image()
            self.pbar.update(1)
        else:
            self.save_annotations_to_file()
            self.root.destroy()

    def clear_classes(self, event=None):
        self.selected_classes = []
        self.update_info_label()

    def quit(self, event=None):
        self.save_annotations_to_file()
        self.root.destroy()

    def save_annotations_to_file(self):
        with open(self.output_file, 'w') as f:
            json.dump(self.annotations, f, indent=4)

    def run(self):
        self.pbar = tqdm(total=len(self.image_files), desc="Annotating images")
        self.root.after(100, self.update_pbar)  # Update progress bar every 100 ms
        self.root.mainloop()
        self.pbar.close()

    def update_pbar(self):
        if self.current_image_index < len(self.image_files):
            self.pbar.update(0)
            update_cadence = int(0.01*len(self.image_files)) 
            self.root.after(update_cadence, self.update_pbar)



def classifierExplainer():
    explanation = """
The script is running in classification mode. This mode allows you to classify images based on the supplied classes.

    Instructions:
        Click on the class buttons to assign a label to the current image
            - You can click on multiple classes for the same image
        Press 'n' to move to the next image 
            - do this if you are done annotating the current image
            - if you click 'n' without selecting a class, the image will be skipped
        Press 'c' to clear all classes for the current image
        Press 'q' to quit the annotation process 
            - this will save the annotations and exit the script
    """
    print(explanation)
    return

