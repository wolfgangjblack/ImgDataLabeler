import cv2, argparse, os, json, random
from PIL import Image
from tqdm import tqdm

def get_image_list(image_dir):
    image_list = []
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            if file.endswith('.jpg') or file.endswith('.png') or file.endswith('.jpeg'):
                image_list.append(os.path.join(root, file))
    random.shuffle(image_list)
    return image_list

class ImageAnnotator:
    def __init__(self, image_files, output_file):
        self.output_file = output_file
        self.annotations = []
        self.image_files = image_files
        self.current_image_index = 0
        self.drawing = False
        self.ix, self.iy = -1, -1
        self.bboxes = []

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
                self.display_image_with_name(img)
                cv2.imshow('Image', img)

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            bbox = [self.ix, self.iy, x, y]
            self.bboxes.append(bbox)
            cv2.rectangle(self.current_image, (self.ix, self.iy), (x, y), (0, 255, 0), 2)
            self.display_image_with_name(self.current_image)
            cv2.imshow('Image', self.current_image)

    def display_image_with_name(self, image):
        image_name = os.path.basename(self.image_files[self.current_image_index])
        # Add padding to the bottom of the image for the name
        padding = 30
        img_with_padding = cv2.copyMakeBorder(image, 0, padding, 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255))
        # Put the image name text below the image
        cv2.putText(img_with_padding, image_name, (10, image.shape[0] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        return img_with_padding


    def save_annotations(self):
        if self.bboxes:
            annotation = {
                'image': self.image_files[self.current_image_index],
                'bboxes': self.bboxes
            }
            self.annotations.append(annotation)
            self.bboxes = []

    def run(self):
        with tqdm(total=len(self.image_files), desc="Annotating images") as pbar:
            while self.current_image_index < len(self.image_files):
                image_path = self.image_files[self.current_image_index]
                self.current_image = cv2.imread(image_path)
                img_with_name = self.display_image_with_name(self.current_image)
                cv2.imshow('Image', img_with_name)
                key = cv2.waitKey(0)

                if key == ord('n'):
                    self.save_annotations()
                    self.current_image_index += 1
                    pbar.update(1)
                elif key == ord('q'):
                    break
                elif key == ord('c'):  # Clear all bboxes for the current image
                    self.bboxes = []
                    self.current_image = cv2.imread(image_path)
                    img_with_name = self.display_image_with_name(self.current_image)
                    cv2.imshow('Image', img_with_name)

        self.save_annotations_to_file()
        cv2.destroyAllWindows()

    def save_annotations_to_file(self):
        with open(self.output_file, 'w') as f:
            json.dump(self.annotations, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Manual Image/Bounding Box Annotation Tool')
    parser.add_argument('--image_dir', type=str, default='./data/testimgs/', help='Directory of images to process')
    parser.add_argument('--output_dir', type=str, default='./data/results/', help='Where to save output data')
    parser.add_argument('--output_file', type=str, default='annotations.json', help='Output file name')

    args = parser.parse_args()

    image_list = get_image_list(args.image_dir)
    output = os.path.join(args.output_dir, args.output_file)
    annotator = ImageAnnotator(image_list, output)
    annotator.run()
