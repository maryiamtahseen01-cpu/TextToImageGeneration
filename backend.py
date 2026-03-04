"""
Imaginify AI Backend Server
This file contains the main backend connection and API endpoints
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from flask_cors import CORS
from datetime import datetime
import os
from bson import ObjectId

# Import database connection
from database import db, users_col, history_col, images_col, subscriptions_col

# ---------------- APP CONFIG ----------------
app = Flask(__name__, static_folder='.', static_url_path='')

# Load configuration
from config import config
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False  # Token never expires for demo

# CORS Configuration - Allow frontend to connect
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# ---------------- DATABASE INITIALIZATION ----------------
def initialize_database():
    """Initialize database with collections and indexes before any user interaction"""
    if db is None:
        print("⚠️ Database not available, skipping initialization")
        return
    
    try:
        print("\n🔧 Initializing Database...")
        print("=" * 60)
        
        # Get existing collections
        existing_collections = db.list_collection_names()
        print(f"📋 Existing collections: {existing_collections if existing_collections else 'None'}")
        
        # Define collections with descriptions
        collections_to_create = {
            "users": "User accounts and profiles",
            "history": "User prompt history",
            "images": "Generated images data",
            "subscriptions": "User subscription plans and payments"
        }
        
        print("\n📦 Creating Collections...")
        for collection_name, description in collections_to_create.items():
            if collection_name not in existing_collections:
                db.create_collection(collection_name)
                print(f"  ✅ Created: {collection_name} - {description}")
            else:
                print(f"  ✓ Exists: {collection_name}")
        
        # Create indexes for performance
        print("\n🔍 Creating Indexes...")
        
        # Users collection indexes
        try:
            users_col.create_index("email", unique=True)
            print("  ✓ users.email (unique)")
        except:
            print("  ✓ users.email (already exists)")
        
        # History collection indexes
        history_col.create_index("user_email")
        history_col.create_index("created_at")
        print("  ✓ history.user_email, history.created_at")
        
        # Images collection indexes
        images_col.create_index("user_email")
        images_col.create_index("created_at")
        print("  ✓ images.user_email, images.created_at")
        
        # Subscriptions collection indexes
        subscriptions_col.create_index("user_email")
        subscriptions_col.create_index("status")
        subscriptions_col.create_index("created_at")
        print("  ✓ subscriptions.user_email, subscriptions.status")
        
        # Show database statistics
        print("\n📊 Database Status:")
        print(f"  - Users: {users_col.count_documents({})} records")
        print(f"  - History: {history_col.count_documents({})} records")
        print(f"  - Images: {images_col.count_documents({})} records")
        print(f"  - Subscriptions: {subscriptions_col.count_documents({})} records")
        
        print("\n✅ Database initialization completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        print("=" * 60)

# Auto-initialize database on server startup
if db is not None:
    initialize_database()

# ---------------- SERVE HTML FILES ----------------
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/login.html')
def serve_login():
    return send_from_directory('.', 'login.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# ---------------- HEALTH CHECK ----------------
@app.route("/api/health")
def health():
    if db is not None:
        try:
            from database import db_connection
            db_connection.client.server_info()
            return jsonify({"status": "success", "message": "MongoDB connected successfully ✅"})
        except:
            return jsonify({"status": "error", "message": "MongoDB disconnected"}), 503
    return jsonify({"status": "warning", "message": "Running without database"}), 200

# ---------------- REGISTER ----------------
@app.route("/api/auth/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        data = request.json
        
        # Validate input
        if not data or not data.get("email") or not data.get("password") or not data.get("name"):
            return jsonify({"status": "error", "error": "Missing required fields"}), 400
        
        # Check if database is available
        if db is None:
            return jsonify({"status": "error", "error": "Database not available"}), 503
        
        # Check if user exists
        if users_col.find_one({"email": data["email"]}):
            return jsonify({"status": "error", "error": "User already exists"}), 400

        # Hash password
        hashed_pw = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

        # Create user
        user_data = {
            "name": data.get("name"),
            "email": data["email"],
            "password": hashed_pw,
            "phone": data.get("phone", ""),
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        result = users_col.insert_one(user_data)
        
        # Create token
        token = create_access_token(identity=data["email"])
        
        return jsonify({
            "status": "success",
            "message": "User registered successfully",
            "token": token,
            "user": {
                "name": data["name"],
                "email": data["email"]
            }
        }), 201
        
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

# ---------------- LOGIN ----------------
@app.route("/api/auth/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        data = request.json
        
        # Validate input
        if not data or not data.get("email") or not data.get("password"):
            return jsonify({"status": "error", "error": "Email and password required"}), 400
        
        # Check if database is available
        if db is None:
            return jsonify({"status": "error", "error": "Database not available"}), 503
        
        # Find user
        user = users_col.find_one({"email": data["email"]})

        if user and bcrypt.check_password_hash(user["password"], data["password"]):
            # Create token
            token = create_access_token(identity=user["email"])
            
            return jsonify({
                "status": "success",
                "message": "Login successful",
                "token": token,
                "user": {
                    "name": user.get("name"),
                    "email": user["email"],
                    "id": str(user["_id"])
                }
            }), 200

        return jsonify({"status": "error", "error": "Invalid email or password"}), 401
        
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

# ---------------- PROTECTED ROUTE ----------------
@app.route("/api/profile", methods=["GET", "OPTIONS"])
@jwt_required()
def profile():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        email = get_jwt_identity()
        
        if db is None:
            return jsonify({"status": "error", "error": "Database not available"}), 503
        
        user = users_col.find_one({"email": email})
        
        if not user:
            return jsonify({"status": "error", "error": "User not found"}), 404
        
        return jsonify({
            "status": "success",
            "user": {
                "name": user.get("name"),
                "email": user["email"],
                "phone": user.get("phone", ""),
                "created_at": user["created_at"].isoformat() if "created_at" in user else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

# Update Profile
@app.route("/api/profile/update", methods=["PUT", "OPTIONS"])
@jwt_required()
def update_profile():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        email = get_jwt_identity()
        data = request.json
        
        if db is None:
            return jsonify({"status": "error", "error": "Database not available"}), 503
        
        # Prepare update data
        update_data = {}
        if "name" in data:
            update_data["name"] = data["name"]
        if "email" in data and data["email"] != email:
            # Check if new email already exists
            existing = users_col.find_one({"email": data["email"]})
            if existing:
                return jsonify({"status": "error", "error": "Email already in use"}), 400
            update_data["email"] = data["email"]
        if "phone" in data:
            update_data["phone"] = data["phone"]
        
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            
            # Update user
            result = users_col.update_one(
                {"email": email},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return jsonify({
                    "status": "success",
                    "message": "Profile updated successfully"
                }), 200
            else:
                return jsonify({
                    "status": "success",
                    "message": "No changes made"
                }), 200
        else:
            return jsonify({"status": "error", "error": "No update data provided"}), 400
        
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500



# ---------------- SAVE EDITED IMAGE ----------------
@app.route("/api/save-image", methods=["POST", "OPTIONS"])
@jwt_required()
def save_edited_image():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        email = get_jwt_identity()
        data = request.json
        
        if not data or not data.get("image_url"):
            return jsonify({"status": "error", "error": "Image URL is required"}), 400
        
        if db is None:
            return jsonify({"status": "error", "error": "Database not available"}), 503
        
        # Get user
        user = users_col.find_one({"email": email})
        if not user:
            return jsonify({"status": "error", "error": "User not found"}), 404
        
        # Prepare image data
        image_data = {
            "user_email": email,
            "user_id": str(user["_id"]),
            "prompt": data.get("prompt", "User edited image"),
            "style": data.get("style", "realistic"),
            "size": data.get("size", "1024x1024"),
            "image_url": data["image_url"],
            "created_at": datetime.utcnow(),
            "type": "edited"  # To distinguish from generated images
        }
        
        # Insert into images collection
        result = images_col.insert_one(image_data)
        
        # Also save to history
        history_data = {
            "user_email": email,
            "prompt": data.get("prompt", "User edited image"),
            "type": "edit",
            "created_at": datetime.utcnow()
        }
        history_col.insert_one(history_data)
        
        return jsonify({
            "status": "success",
            "message": "Image saved successfully",
            "image_id": str(result.inserted_id)
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


# ---------------- SAVE HISTORY ----------------
@app.route("/api/history", methods=["POST", "OPTIONS"])
@jwt_required()
def save_history():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        email = get_jwt_identity()
        data = request.json
        
        if not data or not data.get("prompt"):
            return jsonify({"status": "error", "error": "Prompt is required"}), 400
        
        if db is None:
            return jsonify({"status": "error", "error": "Database not available"}), 503
        
        # Create history record
        history_record = {
            "user_email": email,
            "prompt": data["prompt"],
            "timestamp": data.get("timestamp", datetime.utcnow().isoformat()),
            "created_at": datetime.utcnow()
        }
        
        # Insert into database
        result = history_col.insert_one(history_record)
        
        return jsonify({
            "status": "success",
            "message": "History saved successfully",
            "history_id": str(result.inserted_id)
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

# ---------------- GET HISTORY ----------------
@app.route("/api/history", methods=["GET", "OPTIONS"])
@jwt_required()
def get_history():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        email = get_jwt_identity()
        
        if db is None:
            return jsonify({"status": "error", "error": "Database not available"}), 503
        
        history = list(history_col.find({"user_email": email}).sort("created_at", -1).limit(50))
        
        # Convert ObjectId to string
        for item in history:
            item["_id"] = str(item["_id"])
            if "created_at" in item:
                item["created_at"] = item["created_at"].isoformat()
        
        return jsonify({
            "status": "success",
            "history": history
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


# ---------------- DELETE HISTORY ITEM ----------------
@app.route("/api/history/<history_id>", methods=["DELETE", "OPTIONS"])
@jwt_required()
def delete_history_item(history_id):
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        email = get_jwt_identity()
        
        if db is None:
            return jsonify({"status": "error", "error": "Database not available"}), 503
        
        # Find and delete the history item by ID
        result = history_col.delete_one({"_id": ObjectId(history_id), "user_email": email})
        
        if result.deleted_count == 0:
            return jsonify({"status": "error", "error": "History item not found"}), 404
        
        return jsonify({
            "status": "success",
            "message": "History item deleted successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


# ---------------- CLEAR ALL HISTORY ----------------
@app.route("/api/history", methods=["DELETE", "OPTIONS"])
@jwt_required()
def clear_history():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        email = get_jwt_identity()
        
        if db is None:
            return jsonify({"status": "error", "error": "Database not available"}), 503
        
        # Delete all history for the user
        result = history_col.delete_many({"user_email": email})
        
        return jsonify({
            "status": "success",
            "message": f"{result.deleted_count} history items cleared successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

# ---------------- GET IMAGES ----------------
@app.route("/api/images", methods=["GET", "OPTIONS"])
@jwt_required()
def get_images():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        email = get_jwt_identity()
        
        if db is None:
            return jsonify({"status": "error", "error": "Database not available"}), 503
        
        images = list(images_col.find({"user_email": email}).sort("created_at", -1).limit(50))
        
        # Convert ObjectId to string
        for item in images:
            item["_id"] = str(item["_id"])
            if "created_at" in item:
                item["created_at"] = item["created_at"].isoformat()
        
        return jsonify({
            "status": "success",
            "images": images,
            "count": len(images)
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

# ---------------- SUBSCRIPTION ENDPOINTS ----------------

# Create/Update Subscription
@app.route("/api/subscription", methods=["POST", "OPTIONS"])
@jwt_required()
def create_subscription():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        data = request.json
        email = get_jwt_identity()
        
        if not data or not data.get("plan"):
            return jsonify({"status": "error", "error": "Plan is required"}), 400
        
        if db is None:
            return jsonify({"status": "error", "error": "Database not available"}), 503
        
        # Get user
        user = users_col.find_one({"email": email})
        if not user:
            return jsonify({"status": "error", "error": "User not found"}), 404
        
        # Check if user already has a subscription
        existing_sub = subscriptions_col.find_one({"user_email": email, "status": "active"})
        
        if existing_sub:
            # Update existing subscription
            subscriptions_col.update_one(
                {"_id": existing_sub["_id"]},
                {"$set": {
                    "plan": data["plan"],
                    "price": data.get("price", 0),
                    "billing_cycle": data.get("billing_cycle", "monthly"),
                    "updated_at": datetime.utcnow()
                }}
            )
            message = "Subscription updated successfully"
        else:
            # Create new subscription
            subscription_data = {
                "user_email": email,
                "user_id": str(user["_id"]),
                "plan": data["plan"],  # starter, pro, enterprise
                "price": data.get("price", 0),
                "billing_cycle": data.get("billing_cycle", "monthly"),
                "status": "active",
                "payment_method": data.get("payment_method", "card"),
                "card_last4": data.get("card_last4", ""),
                "features": data.get("features", []),
                "started_at": datetime.utcnow(),
                "created_at": datetime.utcnow()
            }
            subscriptions_col.insert_one(subscription_data)
            message = "Subscription created successfully"
        
        # Update user's subscription status
        users_col.update_one(
            {"email": email},
            {"$set": {
                "subscription_plan": data["plan"],
                "subscription_status": "active"
            }}
        )
        
        return jsonify({
            "status": "success",
            "message": message
        }), 201   
        
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

# Get User's Subscription
@app.route("/api/subscription", methods=["GET", "OPTIONS"])
@jwt_required()
def get_subscription():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        email = get_jwt_identity()
        
        if db is None:
            return jsonify({"status": "error", "error": "Database not available"}), 503
        
        subscription = subscriptions_col.find_one({"user_email": email, "status": "active"})
        
        if not subscription:
            return jsonify({
                "status": "success",
                "subscription": None,
                "message": "No active subscription found"
            }), 200
        
        # Convert ObjectId to string and datetime to ISO format
        subscription["_id"] = str(subscription["_id"])
        if "created_at" in subscription:
            subscription["created_at"] = subscription["created_at"].isoformat()
        if "started_at" in subscription:
            subscription["started_at"] = subscription["started_at"].isoformat()
        if "updated_at" in subscription:
            subscription["updated_at"] = subscription["updated_at"].isoformat()
        
        return jsonify({
            "status": "success",
            "subscription": subscription
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

# Cancel Subscription
@app.route("/api/subscriptions/cancel", methods=["POST", "OPTIONS"])
@jwt_required()
def cancel_subscription():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        email = get_jwt_identity()
        
        if db is None:
            return jsonify({"status": "error", "error": "Database not available"}), 503
        
        # Update subscription status
        result = subscriptions_col.update_one(
            {"user_email": email, "status": "active"},
            {"$set": {
                "status": "cancelled",
                "cancelled_at": datetime.utcnow()
            }}
        )
        
        if result.modified_count == 0:
            return jsonify({"status": "error", "error": "No active subscription found"}), 404
        
        # Update user's subscription status
        users_col.update_one(
            {"email": email},
            {"$set": {"subscription_status": "cancelled"}}
        )
        
        return jsonify({
            "status": "success",
            "message": "Subscription cancelled successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

# Get All Subscriptions (Admin)
@app.route("/api/subscriptions/all", methods=["GET", "OPTIONS"])
@jwt_required()
def get_all_subscriptions():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        if db is None:
            return jsonify({"status": "error", "error": "Database not available"}), 503
        
        subscriptions = list(subscriptions_col.find({}).sort("created_at", -1))
        
        # Convert ObjectId to string
        for sub in subscriptions:
            sub["_id"] = str(sub["_id"])
            if "created_at" in sub:
                sub["created_at"] = sub["created_at"].isoformat()
            if "started_at" in sub:
                sub["started_at"] = sub["started_at"].isoformat()
        
        return jsonify({
            "status": "success",
            "subscriptions": subscriptions,
            "count": len(subscriptions)
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

# ---------------- RUN ----------------
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🤖 Imaginify AI Backend Server")
    print("="*50)
    print("📍 Server running at: http://localhost:5000")
    print("📍 Login page: http://localhost:5000/login.html")
    print("📍 Home page: http://localhost:5000/")
    print("📍 API Health: http://localhost:5000/api/health")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)