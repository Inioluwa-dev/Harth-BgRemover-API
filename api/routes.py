"""
API routes for background removal
"""

from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from PIL import Image
import io

from models.session_manager import SessionManager
from models.human_detector import HumanDetector
from services import image_processor, background_processor
from config import DEFAULT_POSITION, DEFAULT_SCALE, DEFAULT_AUTO_DETECT

router = APIRouter()

# Initialize services
session_manager = SessionManager()
human_detector = HumanDetector()


@router.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Background Removal API is running 🚀 (with auto human detection)"}


@router.post("/remove-bg/")
async def remove_bg(
    file: UploadFile = File(...),
    return_mask: bool = Query(False, description="If true, return only mask instead of PNG with alpha"),
):
    """
    Remove background from an image.
    
    Args:
        file: Image file to process
        return_mask: If true, return only mask instead of PNG with alpha
        auto_detect: Auto-detect human and use optimal model
        
    Returns:
        PNG image with removed background or mask
    """
    try:
        # Read image file
        contents = await file.read()
        
        # Auto-detect and get optimal session
        session, model_name = session_manager.get_optimal_session(contents, human_detector)
        
        if session is None:
            raise HTTPException(status_code=500, detail="Model not available")
        
        # Remove background
        output = image_processor.remove_background(contents, session)
        
        if return_mask:
            # Convert to mask (grayscale)
            img = image_processor.bytes_to_pil(output).convert("RGBA")
            mask = image_processor.get_alpha_channel(img)
            
            img_bytes = image_processor.pil_to_bytes(mask)
            return StreamingResponse(
                img_bytes, 
                media_type="image/png", 
                headers={"Content-Disposition": "attachment; filename=mask.png"}
            )
        else:
            # Return image with removed background
            return StreamingResponse(
                io.BytesIO(output), 
                media_type="image/png", 
                headers={"Content-Disposition": "attachment; filename=removed_bg.png"}
            )

    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@router.post("/add-background/")
async def add_background(
    file: UploadFile = File(..., description="Main image to process"),
    background: UploadFile = File(..., description="Background image to add"),
    position: str = Query(DEFAULT_POSITION, description="Position: 'center', 'top', 'bottom', 'left', 'right', 'top-left', 'top-right', 'bottom-left', 'bottom-right'"),
    scale: str = Query(DEFAULT_SCALE, description="Scale mode: 'cover', 'contain', 'stretch', 'fill'"),
):
    """
    Add a custom background to an image by removing the current background and replacing it.
    
    Args:
        file: Main image to process
        background: Background image to add
        position: Position of background
        scale: Scale mode for background
        auto_detect: Auto-detect human and use optimal model
        
    Returns:
        PNG image with custom background
    """
    try:
        # Read main image
        main_contents = await file.read()
        main_image = Image.open(io.BytesIO(main_contents)).convert("RGBA")
        orig_size = main_image.size

        # Read background image
        bg_contents = await background.read()
        background_image = Image.open(io.BytesIO(bg_contents)).convert("RGB")

        # Auto-detect and get optimal session
        session, model_name = session_manager.get_optimal_session(main_contents, human_detector)
        
        if session is None:
            raise HTTPException(status_code=500, detail="Model not available")

        # Remove background from main image
        foreground = image_processor.remove_background(main_contents, session)
        foreground_img = image_processor.bytes_to_pil(foreground).convert("RGBA")

        # Resize background to match main image size
        background_resized = background_processor.resize_background(
            background_image, orig_size, scale, position
        ).convert("RGBA")

        # Create a new image with the background as base
        result = Image.new("RGBA", orig_size, (0, 0, 0, 0))
        
        # Paste background first
        result.paste(background_resized, (0, 0))
        
        # Then composite the foreground on top
        result = Image.alpha_composite(result, foreground_img)

        # Return result
        img_bytes = image_processor.pil_to_bytes(result)
        return StreamingResponse(
            img_bytes, 
            media_type="image/png", 
            headers={"Content-Disposition": "attachment; filename=added_background.png"}
        )

    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@router.post("/extract-background/")
async def extract_background(
    file: UploadFile = File(...),
):
    """
    Extract the background itself (inverse of the foreground mask).
    
    Args:
        file: Image file to process
        auto_detect: Auto-detect human and use optimal model
        
    Returns:
        PNG image containing only the background portion
    """
    try:
        # Read image file
        contents = await file.read()
        original_image = Image.open(io.BytesIO(contents)).convert("RGBA")

        # Auto-detect and get optimal session
        session, model_name = session_manager.get_optimal_session(contents, human_detector)
        
        if session is None:
            raise HTTPException(status_code=500, detail="Model not available")

        # Remove background to get foreground
        foreground = image_processor.remove_background(contents, session)
        foreground_img = image_processor.bytes_to_pil(foreground).convert("RGBA")

        # Get alpha channel as mask
        alpha = image_processor.get_alpha_channel(foreground_img)
        
        # Create inverse mask (background mask)
        inverse_alpha = image_processor.create_inverse_mask(alpha)
        
        # Apply inverse mask to original image to get background
        background_img = original_image.copy()
        background_img.putalpha(inverse_alpha)

        # Return background image
        img_bytes = image_processor.pil_to_bytes(background_img)
        return StreamingResponse(
            img_bytes, 
            media_type="image/png", 
            headers={"Content-Disposition": "attachment; filename=background.png"}
        )

    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
