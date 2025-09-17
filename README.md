# Background Removal API

This project is a FastAPI backend for removing image backgrounds using the U²-Net deep learning model.

## Features

- Upload an image and get a PNG with the background removed
- Uses the official U²-Net model architecture and weights
- Designed for use with React/Vite frontend or API clients (curl, Postman)

## Requirements

See `requirements.txt` for dependencies.

## Credits

- U²-Net model by Xuebin Qin et al. ([GitHub](https://github.com/xuebinqin/U-2-Net))
- Thanks to the original authors for their open-source work

## License

See `LICENSE` for details. This code is proprietary—do not clone or redistribute.

## Usage

1. Install dependencies from `requirements.txt`
2. Download the official U²-Net weights and place in `models/u2net.pth`
3. Run the server: `uvicorn app:app --host 0.0.0.0 --port 8000`
4. Use Postman or curl to POST an image to `/remove-bg/`

---

**Do not clone or copy this code. It is proprietary and for personal use only.**
