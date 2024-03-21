import os
import logging
import shutil
import psycopg2


def process_image(image_path, detection_model, conn):
    logging.info(f"Starting to process image: {image_path}")
    crop_directory = 'runs/detect/predict/crops'
    predict_directory = 'runs'
    clothing_types = ['bag', 'dress', 'hat', 'jacket', 'pants', 'shirt', 'shoe', 'short', 'skirt']

    try:
        detection_model.predict(source=image_path, conf=0.5, save=True, line_width=2, show_labels=True, save_crop=True)
        logging.info("Image prediction completed successfully")
    except Exception as e:
        logging.error(f"Error during image prediction: {e}")
        raise

    for clothing_type in clothing_types:
        logging.info(f"Processing clothing type: {clothing_type}")
        source_crops_folder = os.path.join(crop_directory, clothing_type)
        if os.path.exists(source_crops_folder):
            for crop_img in os.listdir(source_crops_folder):
                source_path = os.path.join(source_crops_folder, crop_img)
                # Insert the image into the database
                insert_image(clothing_type, source_path, conn)

    # Remove predict directory after processing all crops
    if os.path.exists(predict_directory):
        shutil.rmtree(predict_directory)
        logging.info(f"Predict directory {predict_directory} removed successfully")


def convert_to_binary(file_path):
    logging.debug(f"Converting file to binary: {file_path}")
    with open(file_path, 'rb') as file:
        binary_data = file.read()
    return binary_data


def insert_image(clothing_type, file_path, conn):
    binary_data = convert_to_binary(file_path)
    table_name = f"table_{clothing_type}"
    logging.info(f"Inserting image into table: {table_name}, file path: {file_path}")
    try:
        cur = conn.cursor()
        cur.execute(f"INSERT INTO {table_name} (image_data) VALUES (%s)", (binary_data,))
        conn.commit()
        logging.info(f"Image inserted into {table_name} successfully")
    except psycopg2.Error as e:
        logging.error(f"Error inserting image into {table_name}: {e}")
        conn.rollback()
    finally:
        cur.close()
