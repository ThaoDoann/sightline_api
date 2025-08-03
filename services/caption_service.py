import logging
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import io
from datetime import datetime
from fastapi import HTTPException
from database.connection import get_database
from database.dbmodels import captions
from config.settings import MODEL_NAME, MAX_CAPTION_LENGTH

logger = logging.getLogger(__name__)

class CaptionService:
    def __init__(self):
        self.processor = None
        self.model = None
        self._load_model()
    
    # Load the BLIP model for image captioning  
    def _load_model(self):
        logger.info("Loading BLIP model...")
        self.processor = BlipProcessor.from_pretrained(MODEL_NAME)
        self.model = BlipForConditionalGeneration.from_pretrained(MODEL_NAME)
        logger.info("BLIP model loaded successfully!")
    
    
    # Generate caption for an image
    async def generate_caption(self, user_id: int, image_data: bytes) -> str:
        try:
            image = Image.open(io.BytesIO(image_data))
            inputs = self.processor(image, return_tensors="pt")
            outputs = self.model.generate(**inputs, max_length=MAX_CAPTION_LENGTH)
            caption_text = self.processor.decode(outputs[0], skip_special_tokens=True)
            
            # Save to database
            database = await get_database()
            query = captions.insert().values(
                user_id=user_id,
                caption=caption_text,
                image_data=image_data,
                timestamp=datetime.utcnow()
            )
            await database.execute(query)
            
            return caption_text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating caption: {str(e)}")
    


    # Get all captions for a user
    async def get_user_captions(self, user_id: int):
        database = await get_database()
        query = captions.select().where(captions.c.user_id == user_id).order_by(captions.c.timestamp.desc())

        return await database.fetch_all(query)

# Create global instance
caption_service = CaptionService()