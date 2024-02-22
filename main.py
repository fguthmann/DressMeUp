from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import shutil
from pathlib import Path

app = FastAPI()


@app.get("/")
async def root():
    return{"data": "You are connecting to our server, you can upload a picture or download an outfit"}


@app.post("/upload/{file_path:path}")
async def upload_image(file: UploadFile = File(...), file_path: str = None):
    # Define a base directory to store uploaded files
    base_dir = Path("uploads")
    # Sanitize/validate the file_path here to prevent directory traversal
    # For simplicity, we're directly joining and ensuring it's within "uploads"
    safe_path = base_dir.joinpath(file_path).resolve()

    if not str(safe_path).startswith(str(base_dir.resolve())):
        raise HTTPException(status_code=400, detail="Invalid file path")

    # Create the directory if it doesn't exist
    safe_path.parent.mkdir(parents=True, exist_ok=True)

    # Define the full path for the new file
    file_location = safe_path.with_name(file.filename)

    # Save the file
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": str(file_location)}


@app.get("/image/{file_path:path}")
async def get_image(file_path: str):
    base_dir = Path("uploads")  # Base directory where files are stored
    # Construct the full path to the file
    full_path = base_dir.joinpath(file_path).resolve()

    # Security: Ensure the constructed path is still within the base_dir to prevent directory traversal
    if not str(full_path).startswith(str(base_dir.resolve())):
        raise HTTPException(status_code=400, detail="Invalid file path")

    # Check if the file exists
    if not full_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(path=full_path)