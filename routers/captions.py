import base64
from fastapi import APIRouter, File, UploadFile, Form, Depends
from auth.jwt_handler import oauth2_scheme
from services.caption_service import caption_service
from models.caption import Caption


router = APIRouter()



# Generate caption for uploaded image and save to database
@router.post("/generate-caption", response_model=Caption)
async def generate_caption(
    user_id: int = Form(...),
    file: UploadFile = File(...), 
    token: str = Depends(oauth2_scheme)
):
    contents = await file.read()
    caption_text = await caption_service.generate_caption(user_id, contents)
    
    return Caption(
        caption=caption_text,
        image_base64=base64.b64encode(contents).decode("utf-8")
    )


# Get all captions for a specific user
@router.get("/captions", response_model=list[Caption])
async def fetch_user_captions(user_id: int, token: str = Depends(oauth2_scheme)):
    rows = await caption_service.get_user_captions(user_id)
    print(f"Retrieved {len(rows)} captions for user {user_id}")

    return [
        Caption(
            id=row["caption_id"],
            caption=row["caption"],
            timestamp=row["timestamp"],
            image_base64=base64.b64encode(row["image_data"]).decode("utf-8")
        )
        for row in rows
    ]


# Get all captions (admin endpoint)
@router.get("/all-captions", response_model=list[Caption])
async def fetch_all_captions(token: str = Depends(oauth2_scheme)):
    rows = await caption_service.get_all_captions()
    return [
        Caption(
            id=row["caption_id"],
            caption=row["caption"],
            timestamp=row["timestamp"],
            image_base64=base64.b64encode(row["image_data"]).decode("utf-8")
        )
        for row in rows
    ]