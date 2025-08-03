import base64
import io
from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException, Query
from auth.jwt_handler import oauth2_scheme
from services.caption_service import caption_service
from models.caption import Caption
from models.requests import DeleteCaptionsRequest
import logging

logger = logging.getLogger(__name__)


router = APIRouter()


# Generate caption for uploaded image and save to database
@router.post("/generate-caption", 
             response_model=Caption,
             summary="Generate image caption",
             description="Upload an image and get AI-generated caption")
async def generate_caption(
    user_id: int = Form(..., gt=0, description="Valid user ID"),
    file: UploadFile = File(..., description="Image file"), 
    token: str = Depends(oauth2_scheme)
):
    try:
        # Validate file extension if filename is provided
        if file.filename:
            file_ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
            allowed_extensions = ['jpg', 'jpeg', 'png']
            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file extension '.{file_ext}'. Only .jpg, .jpeg, and .png files are allowed."
                )
        
        # Read file contents
        contents = await file.read()
        
        # Generate caption
        caption_text = await caption_service.generate_caption(user_id, contents)
        
        return Caption(
            caption=caption_text,
            image_base64=base64.b64encode(contents).decode("utf-8")
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error while processing image")


# Get all captions for a specific user with pagination
@router.get("/captions", 
            response_model=list[Caption],
            summary="Get user captions",
            description="Retrieve paginated list of captions for a specific user")
async def fetch_user_captions(
    user_id: int = Query(..., gt=0, description="Valid user ID"),
    token: str = Depends(oauth2_scheme)
):
    try:
        # Get user captions
        rows = await caption_service.get_user_captions(user_id)
        
        logger.info(f"Retrieved {len(rows)} captions for user {user_id}")

        return [
            Caption(
                id=row["caption_id"],
                caption=row["caption"],
                timestamp=row["timestamp"],
                image_base64=base64.b64encode(row["image_data"]).decode("utf-8")
            )
            for row in rows
        ]
        
    except Exception as e:
        logger.error(f"Error fetching captions for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving captions")


# Delete all captions for a specific user
@router.delete("/all-captions",
               summary="Delete all user captions",
               description="Delete all captions associated with a specific user")
async def delete_user_captions(
    user_id: int = Query(..., gt=0, description="Valid user ID"),
    token: str = Depends(oauth2_scheme)):
    try:
        deleted_count = await caption_service.delete_user_captions(user_id)
        
        logger.info(f"Deleted {deleted_count} captions for user {user_id}")
        
        return {
            # "message": f"Successfully deleted {deleted_count} captions for user {user_id}",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error deleting captions for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting captions")

