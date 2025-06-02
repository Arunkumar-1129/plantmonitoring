# 🌱 How to Start Your Plant Monitoring System Website

## 🚨 **IMPORTANT: Correct Website URL**
Your website runs on: **http://127.0.0.1:5000** (NOT port 8000)

---

## 🚀 **4 Easy Ways to Start Your Website:**

### **Method 1: Double-Click Batch File (EASIEST)**
1. Navigate to: `plant_mongo/plant_mongo/`
2. **Double-click**: `START_WEBSITE.bat`
3. Wait for the server to start
4. Open browser and go to: **http://127.0.0.1:5000**

### **Method 2: Python Launcher (AUTO-OPENS BROWSER)**
1. Navigate to: `plant_mongo/plant_mongo/`
2. **Double-click**: `launch_website.py`
3. Website will automatically open in your browser!

### **Method 3: VS Code Terminal**
1. Open VS Code
2. Open terminal (Ctrl + `)
3. Navigate to project folder:
   ```bash
   cd plant_mongo/plant_mongo
   ```
4. Run the server:
   ```bash
   python app.py
   ```
5. Open browser and go to: **http://127.0.0.1:5000**

### **Method 4: Command Prompt**
1. Open Command Prompt
2. Navigate to your project:
   ```cmd
   cd "C:\Users\Dell\OneDrive\Desktop\pms\plant_mongo\plant_mongo"
   ```
3. Start the server:
   ```cmd
   python app.py
   ```
4. Open browser and go to: **http://127.0.0.1:5000**

---

## 🔧 **Prerequisites (One-time setup):**

### **1. MongoDB Must Be Running**
- **Option A**: Start MongoDB service
  ```cmd
  net start MongoDB
  ```
- **Option B**: Open MongoDB Compass application

### **2. Python Dependencies**
If you get import errors, install dependencies:
```bash
pip install -r requirements.txt
```

---

## 🌐 **Website Access:**

### **Correct URL:**
- ✅ **http://127.0.0.1:5000**
- ❌ ~~http://127.0.0.1:8000~~ (Wrong port)

### **Demo Login:**
- **Username**: `admin`
- **Password**: `admin123`

---

## 🛠 **Troubleshooting:**

### **Problem: "This site can't be reached"**
**Solution**: The server is not running. Use one of the methods above to start it.

### **Problem: "MongoDB connection failed"**
**Solution**: Start MongoDB:
- Windows: `net start MongoDB`
- Or open MongoDB Compass

### **Problem: "Module not found"**
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### **Problem: "Port already in use"**
**Solution**: 
1. Close any running Python processes
2. Restart VS Code
3. Try starting the server again

---

## 📁 **Quick Access Files:**

In your project folder (`plant_mongo/plant_mongo/`), you'll find:

- 🚀 **START_WEBSITE.bat** - Double-click to start (Windows)
- 🌐 **launch_website.py** - Auto-opens browser
- 🔗 **Plant Monitoring System.url** - Bookmark to website
- 📖 **README.md** - Complete documentation

---

## 💡 **Pro Tips:**

1. **Bookmark the URL**: Save `http://127.0.0.1:5000` in your browser
2. **Keep Terminal Open**: Don't close the terminal/command prompt while using the website
3. **MongoDB First**: Always ensure MongoDB is running before starting the website
4. **Use Batch File**: The easiest method is double-clicking `START_WEBSITE.bat`

---

## 🎯 **Remember:**
- The website only works when the Python server is running
- Always use port **5000**, not 8000
- MongoDB must be running first
- The server stops when you close VS Code or the terminal

**Happy Plant Monitoring! 🌱✨**
