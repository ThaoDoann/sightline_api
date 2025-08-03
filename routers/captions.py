import base64
from fastapi import APIRouter, File, UploadFile, Depends
from auth.jwt_handler import oauth2_scheme
from services.caption_service import caption_service
from models.caption import Caption

router = APIRouter()

# Generate caption for uploaded image
@router.post("/caption", response_model=Caption)
async def generate_caption(file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    contents = await file.read()
    caption_text = await caption_service.generate_caption(contents)
    return Caption(caption=caption_text)

# Get all captions
@router.get("/captions", response_model=list[Caption])
async def fetch_captions(token: str = Depends(oauth2_scheme)):
    rows = await caption_service.get_all_captions()
    return [
        Caption(
            id=row["id"],
            caption=row["caption"],
            timestamp=row["timestamp"],
            image_base64=base64.b64encode(row["image_data"]).decode("utf-8")
        )
        for row in rows
    ]