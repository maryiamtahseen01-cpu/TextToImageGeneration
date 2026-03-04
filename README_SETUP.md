# 🤖 Imaginify AI - Backend Setup Guide

## Backend aur Frontend Ko Connect Karna

### 📋 Prerequisites
1. Python 3.8 ya usse upar installed hona chahiye
2. MongoDB installed (local ya Atlas)
3. Koi bhi modern web browser

---

## 🚀 Setup Instructions

### Step 1: Dependencies Install Karein
```bash
pip install -r requirements.txt
```

### Step 2: MongoDB Setup

#### Option A: Local MongoDB (Recommended for testing)
1. MongoDB download karein: https://www.mongodb.com/try/download/community
2. Install karein aur start karein
3. Default connection `mongodb://localhost:27017` already `app.py` mein set hai

#### Option B: MongoDB Atlas (Cloud)
1. MongoDB Atlas account banayein: https://www.mongodb.com/cloud/atlas
2. Free cluster create karein
3. Connection string copy karein
4. `app.py` mein line 35 update karein:
```python
MONGO_URI = "your-mongodb-atlas-connection-string"
```

### Step 3: Backend Server Start Karein
```bash
python app.py
```

Server successfully start ho jayega aur aapko ye messages dikhenge:
```
✅ MongoDB Connected Successfully

==================================================
🤖 Imaginify AI Backend Server
==================================================
📍 Server running at: http://localhost:5000
📍 Login page: http://localhost:5000/login.html
📍 Home page: http://localhost:5000/
📍 API Health: http://localhost:5000/api/health
==================================================
```

---

## 🧪 Testing API

### Method 1: Test HTML Page (Recommended)
1. Browser mein open karein: `http://localhost:5000/test_api.html`
2. Server connection automatically check ho jayegi
3. Saari endpoints ko test kar sakte hain:
   - Health Check
   - Register User
   - Login
   - Get Profile
   - Get History

### Method 2: Login Page
1. Browser mein open karein: `http://localhost:5000/login.html`
2. Signup karke naya account banayein
3. Login karein - ab backend se automatically connect ho jayega

### Method 3: curl Commands
```bash
# Health Check
curl http://localhost:5000/api/health

# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

---

## 📁 Project Structure

```
My AI Project/
│
├── app.py                 # Main Flask backend server (UPDATED)
├── login.html             # Login page with API integration (UPDATED)
├── test_api.html          # API testing page (NEW)
├── index.html             # Main homepage
├── auth.py               # Authentication routes (for SQLAlchemy version)
├── models.py             # Database models
├── config.py             # Configuration
├── requirements.txt      # Python dependencies
└── README_SETUP.md       # Ye file
```

---

## 🔌 API Endpoints

### Public Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Server health check |
| POST | `/api/auth/register` | New user registration |
| POST | `/api/auth/login` | User login |

### Protected Endpoints (JWT Required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/profile` | Get user profile |
| GET | `/api/history` | Get user's prompt history |
| POST | `/api/history` | Save user's prompt to history |
| DELETE | `/api/history` | Clear all user's history |
| DELETE | `/api/history/<history_id>` | Delete specific history item |
| POST | `/api/generate` | Generate AI image |

---

## 🔐 Authentication Flow

1. **Register/Login** → Backend JWT token dega
2. **Token Save** → Frontend localStorage mein save karega
3. **Protected Requests** → Header mein token bhejega:
   ```javascript
   headers: {
     'Authorization': 'Bearer YOUR_TOKEN_HERE'
   }
   ```

---

## ⚠️ Common Issues & Solutions

### Issue 1: MongoDB Connection Error
```
MongoDB Connection Error: ...
```
**Solution:**
- Check karo MongoDB service running hai ya nahi
- Windows: Services mein "MongoDB" check karein
- Ya MongoDB Atlas use karein

### Issue 2: CORS Error in Browser
```
Access to fetch at 'http://localhost:5000/api/...' has been blocked by CORS
```
**Solution:**
- `app.py` mein CORS already configured hai
- Browser cache clear karke try karein
- Incognito/Private window mein test karein

### Issue 3: Port Already in Use
```
Address already in use
```
**Solution:**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

---

## 📝 Environment Variables (Optional)

`.env` file banayein aur ye add karein:
```env
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
MONGO_URI=mongodb://localhost:27017
```

---

## 🎯 Next Steps

1. ✅ Backend server successfully run ho raha hai
2. ✅ Frontend backend se connect ho gaya
3. 📸 Ab aap AI image generation integrate kar sakte hain
4. 🎨 More features add kar sakte hain

---

## 📞 Support

Agar koi problem ho to:
1. Console mein errors check karein (F12)
2. Backend terminal mein logs dekhen
3. `test_api.html` se endpoints test karein

**Happy Coding! 🚀**
