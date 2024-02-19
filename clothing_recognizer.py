import os
import random
import os
import cv2

import shutil
import tqdm
import glob
from ultralytics import YOLO


# Load pre-trained model (if not already loaded)
detection_model = YOLO("yolov8m.pt")  # Adjust model path if necessary

# Directory containing the images
images_directory = 'ClothingRecommendation/images/'

# List all files in the directory
image_files = [f for f in os.listdir(images_directory) if f.endswith('.jpg')]

# Iterate over each file in the directory
for image_file in image_files:
    image_path = os.path.join(images_directory, image_file)  # Construct full image path
    # Perform prediction
    predictions = detection_model.predict(source=image_path, conf=0.5, save=True, line_width=2, show_labels=True,
                                          save_crop=True)

    # Process predictions as needed (e.g., print results, analyze predictions, etc.)
    # This is just a placeholder print statement. You can replace it with your processing code.
    print(f"Processed {image_path}")