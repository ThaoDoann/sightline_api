# Sightline API

This is the backend API for the Sightline application, providing image captioning capabilities using the BLIP model.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python main.py
```

The server will start on http://localhost:8000

## API Endpoints

- `GET /`: Welcome message
- `POST /caption`: Generate caption for an image
  - Accepts multipart/form-data with an image file
  - Returns JSON with the generated caption

## CORS Configuration

The API is configured to accept requests from any origin. In production, you should restrict this to specific origins. 