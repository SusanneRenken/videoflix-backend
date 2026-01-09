# Videoflix – Backend (Django REST Framework)

ideoflix is a Netflix-like video streaming platform.
This backend provides authentication, video upload & processing, and HLS video streaming using FFmpeg and background workers.

---

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quickstart](#quickstart-development)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
  - [Authentication](#authentication)
  - [Video Endpoints](#video-endpoints)
  - [HLS Streaming Endpoints](#hls-streaming-endpoints)
- [Error Handling](#error-handling)
- [Tests & Coverage](#tests--coverage)
- [Project Structure](#project-structure)

---

## Features

- User registration with email activation
- Login & logout using JWT via HttpOnly cookies
- Password reset via email
- Video upload with background processing
- Automatic HLS conversion (480p, 720p, 1080p)
- Thumbnail generation using FFmpeg
- Streaming via HLS (.m3u8 + .ts)
- Clean API structure and consistent error handling

---

## Tech Stack

- Python 3.12  
- Django 5 + DRF  
- PostgreSQL
- Redis + django-rq
- FFmpeg
- Docker & Docker Compose

---

## Installation / Quickstart

### Clone the repository
```bash
git clone <repo-url>
cd videoflix-backend
```

### Rename .env.template and set keys
- Rename `.env.template` to `.env`.
- Open `.env` and set your values:
```bash
SECRET_KEY=your-django-secret-key
DEBUG=True

DB_NAME=videoflix_db
DB_USER=videoflix_user
DB_PASSWORD=videoflix_password
DB_HOST=db
DB_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email_user
EMAIL_HOST_PASSWORD=your_email_password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=videoflix@example.com
```

### Start the project with Docker
```bash
docker-compose up --build
```
The backend will be available at: http://localhost:8000
Admin panel: http://localhost:8000/admin/

---
## Environment Variables

The project uses a `.env` file in the root directory.

Required variables:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Enable debug mode |
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | PostgreSQL user |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_HOST` | Database host (Docker service) |
| `DB_PORT` | Database port |
| `REDIS_HOST` | Redis host |
| `REDIS_PORT` | Redis port |
| `EMAIL_HOST` | SMTP server |
| `EMAIL_HOST_USER` | SMTP username |
| `EMAIL_HOST_PASSWORD` | SMTP password |

---

## API Endpoints
All endpoints require authentication unless stated otherwise.
JWT tokens are handled via HttpOnly cookies.

### Authentication

The project uses JWT authentication via HttpOnly cookies.

Available endpoints:

| Method | Endpoint | Description |
|--------|----------|--------------|
| POST | `/api/register/` | Register a new user and send activation email |
| GET | `/api/activate/{uid}/{token}/` | Activate user account |
| POST | `/api/login/` | Login and set JWT cookies |
| POST | `/api/logout/` | Logout and invalidate refresh token |
| POST | `/api/token/refresh/` | Refresh access token |
| POST | `/api/password_reset/` | Send password reset email |
| POST | `/api/password_confirm/{uid}/{token}/` | Set a new password |


### Video Endpoints

| Method | Endpoint | Description |
|--------|----------|--------------|
| GET | `/api/video/` | List all ready videos |


### Quiz Endpoints

| Method | Endpoint | Description |
|--------|----------|--------------|
| GET | `/api/video/{id}/{resolution}/index.m3u8` | HLS playlist |
| GET | `/api/video/{id}/{resolution}/{segment}.ts` | HLS video segment |

Supported resolutions:
- 480p
- 720p
- 1080p

---

## Error Handling

The API returns clear error messages with appropriate HTTP status codes:

- `400 Bad Request` – invalid input
- `401 Unauthorized` – missing or invalid authentication
- `403 Forbidden` – insufficient permissions
- `404 Not Found` – resource not found
- `500 Internal Server Error` – unexpected server error (uncaught exception during request processing)

---

## Project Structure

```
videoflix-backend/
├── auth_app/
│   ├── api/
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── views.py
│   ├── utils/
│   │   ├── email_activation.py
│   │   ├── reset_password.py
│   ├── apps.py
│   ├── signals.py
├── core/
│   ├── settings.py
│   ├── urls.py
├── video_app/
│   ├── api/
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── views.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── signals.py
│   ├── tasks.py
├── manage.py
└── docker-compose.yml
```
