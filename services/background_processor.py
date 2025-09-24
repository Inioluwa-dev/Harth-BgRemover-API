"""
Background processing utilities
"""

from PIL import Image
import numpy as np
from config import DEFAULT_POSITION, DEFAULT_SCALE


class BackgroundProcessor:
    """Handles background resizing and positioning"""
    
    @staticmethod
    def resize_background(background_img, target_size, scale_mode, position):
        """
        Resize background image to fit target size based on scale mode and position.
        
        Args:
            background_img: PIL Image of background
            target_size: (width, height) tuple for target size
            scale_mode: 'cover', 'contain', 'stretch', 'fill'
            position: Position string
            
        Returns:
            PIL Image resized and positioned according to parameters
        """
        target_w, target_h = target_size
        bg_w, bg_h = background_img.size
        
        if scale_mode == "stretch":
            return background_img.resize(target_size, Image.LANCZOS)
        
        elif scale_mode == "fill":
            scale_w = target_w / bg_w
            scale_h = target_h / bg_h
            scale = max(scale_w, scale_h)
            
            new_w = int(bg_w * scale)
            new_h = int(bg_h * scale)
            resized = background_img.resize((new_w, new_h), Image.LANCZOS)
            
            return BackgroundProcessor._crop_to_position(resized, target_size, position)
        
        elif scale_mode == "contain":
            scale_w = target_w / bg_w
            scale_h = target_h / bg_h
            scale = min(scale_w, scale_h)
            
            new_w = int(bg_w * scale)
            new_h = int(bg_h * scale)
            resized = background_img.resize((new_w, new_h), Image.LANCZOS)
            
            result = Image.new("RGB", target_size, (0, 0, 0))
            paste_position = BackgroundProcessor._get_paste_position(
                (new_w, new_h), target_size, position
            )
            result.paste(resized, paste_position)
            return result
        
        else:  # cover (default)
            scale_w = target_w / bg_w
            scale_h = target_h / bg_h
            scale = max(scale_w, scale_h)
            
            new_w = int(bg_w * scale)
            new_h = int(bg_h * scale)
            resized = background_img.resize((new_w, new_h), Image.LANCZOS)
            
            return BackgroundProcessor._crop_to_position(resized, target_size, position)
    
    @staticmethod
    def _crop_to_position(image, target_size, position):
        """Crop image to target size at specified position"""
        img_w, img_h = image.size
        target_w, target_h = target_size
        
        if position in ["top-left", "left", "bottom-left"]:
            left = 0
        elif position in ["top-right", "right", "bottom-right"]:
            left = img_w - target_w
        else:  # center, top, bottom
            left = (img_w - target_w) // 2
        
        if position in ["top-left", "top", "top-right"]:
            top = 0
        elif position in ["bottom-left", "bottom", "bottom-right"]:
            top = img_h - target_h
        else:  # center, left, right
            top = (img_h - target_h) // 2
        
        right = left + target_w
        bottom = top + target_h
        
        return image.crop((left, top, right, bottom))
    
    @staticmethod
    def _get_paste_position(image_size, target_size, position):
        """Get paste position for centering image on target"""
        img_w, img_h = image_size
        target_w, target_h = target_size
        
        if position in ["top-left", "left", "bottom-left"]:
            x = 0
        elif position in ["top-right", "right", "bottom-right"]:
            x = target_w - img_w
        else:  # center, top, bottom
            x = (target_w - img_w) // 2
        
        if position in ["top-left", "top", "top-right"]:
            y = 0
        elif position in ["bottom-left", "bottom", "bottom-right"]:
            y = target_h - img_h
        else:  # center, left, right
            y = (target_h - img_h) // 2
        
        return (x, y)
