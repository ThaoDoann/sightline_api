# Sightline API

This is the backend API for the Sightline application, providing image captioning capabilities using the BLIP model.

## Setup

### Running on Localhost

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Create new SQLite database:**
```bash
py scripts/init_db.py
```

3. **Run the server:**
```bash
python main.py
```

The server will start on http://localhost:8000

## API Endpoints

### Root
- **`GET /`** - Welcome message and API version

### Authentication (No JWT required)
- **`POST /api/v1/register`** - Register new user
  - **Body:** `{"username": "string", "email": "string", "password": "string"}`
  - **Response:** `{"message": "User registered successfully"}`

- **`POST /api/v1/login`** - User login
  - **Body:** `{"username": "email", "password": "string"}` (form-data)
  - **Response:** `{"access_token": "jwt_token", "token_type": "bearer", "user_id": 1, "username": "string", "email": "string"}`

### Captions (JWT required)
- **`POST /api/v1/generate-caption`** - Generate caption for uploaded image
  - **Headers:** `Authorization: Bearer <jwt_token>`
  - **Body:** `multipart/form-data` with `user_id` and `file`
  - **File types:** JPG, JPEG, PNG
  - **Response:** `{"caption": "string", "image_base64": "string"}`

- **`GET /api/v1/captions?user_id=<id>`** - Get user's caption history
  - **Headers:** `Authorization: Bearer <jwt_token>`
  - **Query params:** `user_id` (required)
  - **Response:** Array of caption objects with images

- **`DELETE /api/v1/all-captions?user_id=<id>`** - Delete all user captions
  - **Headers:** `Authorization: Bearer <jwt_token>`
  - **Query params:** `user_id` (required)
  - **Response:** `{"deleted_count": number}`

### Interactive API Documentation
- **`GET /docs`** - Swagger/OpenAPI interactive documentation
- **`GET /redoc`** - ReDoc API documentation

