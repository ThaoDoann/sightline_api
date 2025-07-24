from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import io
import torch
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sightline API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize BLIP model
logger.info("Loading BLIP model...")
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
logger.info("BLIP model loaded successfully!")

@app.get("/")
async def root():
    return {"message": "Welcome to Sightline API"}

@app.post("/caption")
async def generate_caption(file: UploadFile = File(...)):
    try:
        logger.info(f"Processing image: {file.filename}")
        # Read and validate image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Process image and generate caption
        inputs = processor(image, return_tensors="pt")
        outputs = model.generate(**inputs, max_length=50)
        caption = processor.decode(outputs[0], skip_special_tokens=True)
        
        logger.info(f"Generated caption: {caption}")
        return {"caption": caption}
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # host = "localhost" 
    host = "0.0.0.0"  # Allow access from any IP
    port = 8000
    logger.info(f"Starting server on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port) 