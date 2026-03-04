# Imaginify AI Backend Connection Code

This project implements a Flask-based backend with MongoDB database connection for an AI image generation application.

## Project Structure

- `app.py` - Main entry point (imports all functionality from backend module)
- `backend.py` - Main backend server with all API endpoints
- `database.py` - Database connection management
- `config.py` - Configuration settings
- `.env` - Environment variables
- `requirements.txt` - Python dependencies

## Backend Connection Features

### Database Connection
- MongoDB connection using PyMongo
- Connection pooling and error handling
- Collections: users, history, images, subscriptions
- Automatic database initialization

### Environment Configuration
- JWT authentication with configurable secrets
- MongoDB URI configuration
- CORS settings for frontend integration
- Database connection parameters

### API Endpoints
- User authentication (register, login)
- Profile management
- Image generation and history
- Subscription management
- Health check endpoint

## Environment Variables

The following environment variables are configured in `.env`:
- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT authentication secret
- `MONGO_URI` - MongoDB connection string
- `DATABASE_URL` - SQL database URL (if needed)
- `CORS_ORIGINS` - Allowed origins for CORS

## Running the Application

1. Install dependencies: `pip install -r requirements.txt`
2. Set up MongoDB (local or Atlas)
3. Configure environment variables in `.env`
4. Run the server: `python app.py`

The server will be available at `http://localhost:5000`