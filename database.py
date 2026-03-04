from pymongo import MongoClient
from config import config
import os


class DatabaseConnection:
    def __init__(self):
        self.client = None
        self.db = None
        self.users_col = None
        self.history_col = None
        self.images_col = None
        self.subscriptions_col = None
        
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            # Connect to MongoDB
            self.client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)
            self.client.server_info()  # Test connection
            # Extract database name from MONGO_URI
            db_name = config.MONGO_URI.split('/')[-1] if '/' in config.MONGO_URI else "imaginify_db"
            self.db = self.client[db_name]
            
            # Initialize collections
            self.users_col = self.db["users"]
            self.history_col = self.db["history"]
            self.images_col = self.db["images"]
            self.subscriptions_col = self.db["subscriptions"]
            
            print("✅ MongoDB Connected Successfully")
            return True
        except Exception as e:
            print(f"⚠️ MongoDB Connection Error: {e}")
            print("Running without database connection")
            return False
    
    def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
    
    def get_db(self):
        """Get database instance"""
        return self.db
    
    def get_users_collection(self):
        """Get users collection"""
        return self.users_col
    
    def get_history_collection(self):
        """Get history collection"""
        return self.history_col
    
    def get_images_collection(self):
        """Get images collection"""
        return self.images_col
    
    def get_subscriptions_collection(self):
        """Get subscriptions collection"""
        return self.subscriptions_col


# Create a global instance of the database connection
db_connection = DatabaseConnection()

# Initialize the database connection
if db_connection.connect():
    # Get collection references
    users_col = db_connection.get_users_collection()
    history_col = db_connection.get_history_collection()
    images_col = db_connection.get_images_collection()
    subscriptions_col = db_connection.get_subscriptions_collection()
    db = db_connection.get_db()
else:
    # Set to None if connection fails
    users_col = None
    history_col = None
    images_col = None
    subscriptions_col = None
    db = None