from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import torch
from PIL import Image
import io
import numpy as np
import os
import uuid

# Import U2NET + U2NETP architectures
from u2net import U2NET, U2NETP

app = FastAPI()

# Allow React frontend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # during dev, allow all. In prod, restrict this.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Load Model at Startup
# -------------------------
MODEL_PATH = "models/u2net.pth"

def load_model(path):
    """Try to load U2NET or U2NETP automatically"""
    try:
        # Try full U2NET
        model = U2NET(3, 1)
        model.load_state_dict(torch.load(path, map_location="cpu"))
        print("✅ Loaded U²NET (full)")
        return model
    except Exception as e1:
        try:
            # Try U2NETP
            model = U2NETP(3, 1)
            model.load_state_dict(torch.load(path, map_location="cpu"))
            print("✅ Loaded U²NETP (lite)")
            return model
        except Exception as e2:
            print("❌ Could not load model as U2NET or U2NETP:", e1, e2)
            return None

model = load_model(MODEL_PATH)
if model:
    model.eval()

# -------------------------
# Helpers
# -------------------------
def preprocess(image: Image.Image):
    """Resize and normalize image for U2NET"""
    img = image.resize((320, 320))
    img = np.array(img).astype(np.float32) / 255.0
    img = img.transpose((2, 0, 1))  # HWC → CHW
    img = torch.from_numpy(img).unsqueeze(0)
    return img


def postprocess(mask, orig_size):
    """Convert model mask output to a PIL Image with original size"""
    mask = mask.squeeze().cpu().numpy()
    mask = (mask - mask.min()) / (mask.max() - mask.min() + 1e-8)  # normalize
    mask = (mask * 255).astype(np.uint8)
    mask = Image.fromarray(mask).resize(orig_size, Image.BILINEAR)
    return mask


# -------------------------
# API Routes
# -------------------------
@app.get("/")
async def root():
    return {"message": "Background Removal API is running 🚀"}


@app.post("/remove-bg/")
async def remove_bg(
    file: UploadFile = File(...),
    return_mask: bool = Query(False, description="If true, return only mask instead of PNG with alpha"),
):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    try:
        # Read image file
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        orig_size = image.size

        # Preprocess
        inp = preprocess(image)

        # Inference
        with torch.no_grad():
            d1, *_ = model(inp)
            mask = d1[:, 0, :, :]

        # Postprocess
        mask_img = postprocess(mask, orig_size)

        if return_mask:
            # Return mask image as bytes
            img_bytes = io.BytesIO()
            mask_img.save(img_bytes, format="PNG")
            img_bytes.seek(0)
            return StreamingResponse(img_bytes, media_type="image/png", headers={"Content-Disposition": "attachment; filename=mask.png"})
        else:
            image.putalpha(mask_img)  # apply mask as alpha channel

            # Return image with removed background as bytes
            img_bytes = io.BytesIO()
            image.save(img_bytes, format="PNG")
            img_bytes.seek(0)
            return StreamingResponse(img_bytes, media_type="image/png", headers={"Content-Disposition": "attachment; filename=removed_bg.png"})

    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
