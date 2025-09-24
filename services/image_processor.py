"""
Image processing utilities
"""

from PIL import Image
import io
from rembg import remove


class ImageProcessor:
    """Handles basic image processing operations"""
    
    @staticmethod
    def remove_background(image_bytes, session):
        """
        Remove background from image using rembg
        
        Args:
            image_bytes: Image data as bytes
            session: rembg session
            
        Returns:
            bytes: Image with removed background
        """
        return remove(image_bytes, session=session)
    
    @staticmethod
    def bytes_to_pil(image_bytes):
        """Convert bytes to PIL Image"""
        return Image.open(io.BytesIO(image_bytes))
    
    @staticmethod
    def pil_to_bytes(image, format="PNG"):
        """Convert PIL Image to bytes"""
        img_bytes = io.BytesIO()
        image.save(img_bytes, format=format)
        img_bytes.seek(0)
        return img_bytes
    
    @staticmethod
    def get_alpha_channel(image):
        """Get alpha channel from RGBA image"""
        return image.split()[-1]
    
    @staticmethod
    def create_inverse_mask(alpha_channel):
        """Create inverse mask from alpha channel"""
        return Image.eval(alpha_channel, lambda x: 255 - x)
