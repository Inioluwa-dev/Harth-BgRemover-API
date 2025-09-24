# Background Removal API

This project is a FastAPI backend for removing image backgrounds using AI models with automatic human detection.

## Features

- **Remove Background**: Upload an image and get a PNG with the background removed
- **Add Custom Background**: Replace the background with a custom image
- **Extract Background**: Get just the background portion of an image (inverse of foreground)
- **Fast Processing**: Optimized for speed with `isnet-general-use` as primary model
- **Smart Fallback**: Automatically falls back to `u2net_human_seg` only when needed
- Designed for use with React/Vite frontend or API clients (curl, Postman)

## API Endpoints

### 1. Remove Background
- **POST** `/remove-bg/`
- **Parameters**: 
  - `file`: Image file to process
  - `return_mask`: (optional) If true, returns only the mask instead of PNG with alpha
- **Returns**: PNG image with transparent background

### 2. Add Custom Background
- **POST** `/add-background/`
- **Parameters**:
  - `file`: Main image to process
  - `background`: Background image to add
  - `position`: (optional) Position of background - 'center', 'top', 'bottom', 'left', 'right', 'top-left', 'top-right', 'bottom-left', 'bottom-right' (default: 'center')
  - `scale`: (optional) Scale mode - 'cover', 'contain', 'stretch', 'fill' (default: 'cover')
- **Returns**: PNG image with custom background

### 3. Extract Background
- **POST** `/extract-background/`
- **Parameters**:
  - `file`: Image file to process
- **Returns**: PNG image containing only the background portion

## Performance

- **Primary Model**: `isnet-general-use` (fast, works great for most images)
- **Fallback Model**: `u2net_human_seg` (slower, only used if primary fails)
- **Optimized**: Image resizing and fast detection for maximum speed

## Requirements

See `requirements.txt` for dependencies.

## Credits

- U²-Net model by Xuebin Qin et al. ([GitHub](https://github.com/xuebinqin/U-2-Net))
- Thanks to the original authors for their open-source work

## License

See `LICENSE` for details. This code is proprietary—do not clone or redistribute.

---

**Done by Mr Heritage (Olayoriju Inioluwa)**

**Do not clone or copy this code. It is proprietary and for personal use only.**
