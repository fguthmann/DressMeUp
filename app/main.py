import aiofiles
import base64
import logging
import os
import psycopg2
import shutil
from initialization_database import initialize_database, db_params
from image_processing import process_image
from clothes_recommendations import pick_outfit
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from ultralytics import YOLO


app = FastAPI()

# Directory where uploaded files will be stored
UPLOAD_DIRECTORY = "./static/uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# Serve files from the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def upload_form():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    initialize_database()
    logging.info("Database initialized")

    return """
    <html>
        <body>
        <h1>Upload an image</h1>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input name="file" type="file" accept="image/*">
                <input type="submit">
            </form>

             <h1>Enter Temperature in Celsius</h1>
            <form action="/temperature" method="get">
                <input name="temp_celsius" type="text" placeholder="Temperature in Celsius">
                <input type="submit" value="Submit">
            </form>
        </body>
    </html>
    """


@app.post("/upload")
async def handle_upload(file: UploadFile = File(...)):
    file_location = f"{UPLOAD_DIRECTORY}/{file.filename}"
    logging.info(f"Handling file upload: {file.filename}")

    try:
        detection_model = YOLO('app/best.pt')
        logging.info("YOLO model loaded successfully")
    except Exception as e:
        logging.error(f"Failed to load model: {e}")
        raise HTTPException(status_code=500, detail="Model loading failed")
    async with aiofiles.open(file_location, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
        logging.info(f"File saved: {file_location}")

    # Establish database connection
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    # Process and insert the image into the database
    try:
        process_image(file_location, detection_model, conn)
        logging.info("Image processed and inserted into the database successfully")
    except Exception as e:
        logging.error(f"Error processing and inserting image: {e}")
        raise HTTPException(status_code=500, detail="Error processing and inserting image")

    finally:
        cur.close()
        conn.close()
    remove_folder_static()

    return {"info": f"File '{file.filename}' uploaded successfully, and processed for database insertion.", "filepath": f"/static/{file.filename}"}


def remove_folder_static():
    if os.path.exists('static'):
        shutil.rmtree('static')


@app.get("/temperature", response_class=HTMLResponse)
async def display_temperature(temp_celsius: float):
    logging.info(f"Fetching outfit for temperature: {temp_celsius}°C")
    try:
        outfit = pick_outfit(temp_celsius, db_params)
        images_html = ""
        for clothing_item, image_data in outfit.items():
            if image_data:
                # Convert binary image data to Base64 for embedding
                base64_encoded_data = base64.b64encode(image_data).decode('utf-8')
                image_html = f'<img src="data:image/jpeg;base64,{base64_encoded_data}" alt="{clothing_item}' \
                             f'" style="width:100px; height:100px; margin:10px;">'
                images_html += f'<div>{clothing_item.capitalize()}: {image_html}</div>'
            else:
                images_html += f'<div>{clothing_item.capitalize()}: Image not available.</div>'
    except Exception as e:
        logging.error(f"Error fetching outfit: {e}")
        raise HTTPException(status_code=500, detail="Error fetching outfit")

    return f"""
        <html>
            <head>
                <title>Temperature Result</title>
            </head>
            <body>
                <h1>Recommended Outfit</h1>
                <div style="display:flex; flex-wrap:wrap;">
                    {images_html}
                </div>
            </body>
        </html>
        """
