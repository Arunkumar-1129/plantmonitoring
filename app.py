from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient, errors
from bson import ObjectId
import logging
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
CORS(app)  # Enable CORS

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection setup with error handling
try:
    # MongoDB connection with timeout and error handling
    client = MongoClient(
        'mongodb://localhost:27017/',
        serverSelectionTimeoutMS=5000,  # 5 second timeout
        connectTimeoutMS=10000,         # 10 second connection timeout
        socketTimeoutMS=20000           # 20 second socket timeout
    )

    # Test the connection
    client.admin.command('ping')
    logger.info("✅ Successfully connected to MongoDB!")

    db = client['plant_diseases']

except errors.ServerSelectionTimeoutError as e:
    logger.error(f"❌ MongoDB connection failed: {e}")
    logger.error("Please ensure MongoDB is running on localhost:27017")
    db = None
except Exception as e:
    logger.error(f"❌ Unexpected MongoDB error: {e}")
    db = None

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.email = user_data['email']
        self.first_name = user_data.get('first_name', '')
        self.last_name = user_data.get('last_name', '')

@login_manager.user_loader
def load_user(user_id):
    if db is None:
        return None
    user_data = db.users.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

def init_db():
    # Check if collections exist, if not create them
    if 'diseases' not in db.list_collection_names():
        db.create_collection('diseases')

    if 'solutions' not in db.list_collection_names():
        db.create_collection('solutions')

    if 'users' not in db.list_collection_names():
        db.create_collection('users')
        # Create a demo admin user
        admin_user = {
            'username': 'admin',
            'email': 'admin@example.com',
            'password': generate_password_hash('admin123'),
            'first_name': 'Admin',
            'last_name': 'User'
        }
        db.users.insert_one(admin_user)
    
    # Insert sample data if collections are empty
    if db.diseases.count_documents({}) == 0:
        sample_data = [
            {
                "name": "powdery mildew",
                "description": "A fungal disease that appears as white powdery spots on leaves and stems",
                "image": "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&h=300&fit=crop&q=80",
                "solutions": [
                    {
                        "type": "organic",
                        "solution": "Mix 1 tablespoon baking soda with 1 gallon of water",
                        "image": "https://images.unsplash.com/photo-1584464491033-06628f3a6b7b?w=300&h=200&fit=crop&q=80",
                        "effectiveness": "High",
                        "application": "Spray on affected areas every 7-10 days"
                    },
                    {
                        "type": "organic",
                        "solution": "Apply milk spray (40% milk to 60% water)",
                        "image": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=300&h=200&fit=crop&q=80",
                        "effectiveness": "Medium",
                        "application": "Spray early morning or evening"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Apply potassium bicarbonate fungicides",
                        "image": "https://images.unsplash.com/photo-1582719471384-894fbb16e074?w=300&h=200&fit=crop&q=80",
                        "effectiveness": "Very High",
                        "application": "Follow manufacturer's instructions"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Use synthetic fungicides containing myclobutanil",
                        "image": "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=300&h=200&fit=crop&q=80",
                        "effectiveness": "Very High",
                        "application": "Professional application recommended"
                    }
                ]
            },
            {
                "name": "blight",
                "description": "A plant disease causing browning and death of plant tissues",
                "image": "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&h=300&fit=crop&q=80",
                "solutions": [
                    {
                        "type": "organic",
                        "solution": "Apply copper-based fungicides",
                        "image": "https://images.unsplash.com/photo-1628771065518-0d82f1938462?w=300&h=200&fit=crop&q=80",
                        "effectiveness": "High",
                        "application": "Apply during dry weather conditions"
                    },
                    {
                        "type": "organic",
                        "solution": "Use Bacillus subtilis biological fungicide",
                        "image": "https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?w=300&h=200&fit=crop&q=80",
                        "effectiveness": "Medium",
                        "application": "Apply as preventive measure"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Apply chlorothalonil every 7-10 days",
                        "image": "https://images.unsplash.com/photo-1576086213369-97a306d36557?w=300&h=200&fit=crop&q=80",
                        "effectiveness": "Very High",
                        "application": "Regular scheduled applications"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Use mancozeb or maneb fungicides",
                        "image": "https://images.unsplash.com/photo-1582719471384-894fbb16e074?w=300&h=200&fit=crop&q=80",
                        "effectiveness": "Very High",
                        "application": "Follow safety guidelines strictly"
                    }
                ]
            },
            {
                "name": "rust",
                "description": "A fungal disease causing orange or rust-colored spots on leaves",
                "image": "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&h=300&fit=crop&q=80",
                "solutions": [
                    {
                        "type": "organic",
                        "solution": "Apply sulfur dust or spray early in the season",
                        "image": "https://images.unsplash.com/photo-1574263867128-a3d5c1b1deae?w=300&h=200&fit=crop&q=80",
                        "effectiveness": "High",
                        "application": "Early morning application preferred"
                    },
                    {
                        "type": "organic",
                        "solution": "Use neem oil every 7-14 days",
                        "image": "https://images.unsplash.com/photo-1628771065518-0d82f1938462?w=300&h=200&fit=crop&q=80",
                        "effectiveness": "Medium",
                        "application": "Avoid application during hot weather"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Apply myclobutanil or propiconazole fungicides",
                        "image": "https://images.unsplash.com/photo-1576086213369-97a306d36557?w=300&h=200&fit=crop&q=80",
                        "effectiveness": "Very High",
                        "application": "Professional consultation recommended"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Use tebuconazole for severe infections",
                        "image": "https://images.unsplash.com/photo-1582719471384-894fbb16e074?w=300&h=200&fit=crop&q=80",
                        "effectiveness": "Very High",
                        "application": "Last resort for severe cases"
                    }
                ]
            },
            {
                "name": "aphid infestation",
                "description": "Small insects that feed on plant sap, causing yellowing and stunted growth",
                "image": "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&h=300&fit=crop&q=80",
                "solutions": [
                    {
                        "type": "organic",
                        "solution": "Spray with insecticidal soap solution",
                        "image": "https://images.unsplash.com/photo-1584464491033-06628f3a6b7b?w=300&h=200&fit=crop&q=80",
                        "effectiveness": "High",
                        "application": "Apply every 3-5 days until controlled"
                    },
                    {
                        "type": "organic",
                        "solution": "Release ladybugs as natural predators",
                        "image": "https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?w=300&h=200&fit=crop&q=80",
                        "effectiveness": "Very High",
                        "application": "Release in early morning or evening"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Apply systemic insecticides like imidacloprid",
                        "image": "https://images.unsplash.com/photo-1576086213369-97a306d36557?w=300&h=200&fit=crop&q=80",
                        "effectiveness": "Very High",
                        "application": "Follow label instructions carefully"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Use pyrethroid-based contact insecticides",
                        "image": "https://images.unsplash.com/photo-1582719471384-894fbb16e074?w=300&h=200&fit=crop&q=80",
                        "effectiveness": "High",
                        "application": "Apply during cooler parts of the day"
                    }
                ]
            },
            {
                "name": "black spot",
                "description": "Fungal disease causing black spots on leaves, common in roses",
                "image": "https://images.unsplash.com/photo-1574263867128-a3d5c1b1deae?w=400&h=300&fit=crop&q=80",
                "solutions": [
                    {
                        "type": "organic",
                        "solution": "Apply baking soda and oil spray",
                        "image": "https://images.unsplash.com/photo-1628771065518-0d82f1938462?w=300&h=200&fit=crop&q=80",
                        "effectiveness": "Medium",
                        "application": "Spray weekly during growing season"
                    },
                    {
                        "type": "organic",
                        "solution": "Use compost tea as foliar spray",
                        "image": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=300&h=200&fit=crop&q=80",
                        "effectiveness": "Medium",
                        "application": "Apply every 2 weeks"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Apply triazole fungicides",
                        "image": "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=300&h=200&fit=crop&q=80",
                        "effectiveness": "Very High",
                        "application": "Start applications early in season"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Use copper-based fungicides",
                        "image": "https://images.unsplash.com/photo-1582719471384-894fbb16e074?w=300&h=200&fit=crop&q=80",
                        "effectiveness": "High",
                        "application": "Apply before symptoms appear"
                    }
                ]
            }
        ]

        db.diseases.insert_many(sample_data)

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username and password:
            user_data = db.users.find_one({'username': username})
            if user_data and check_password_hash(user_data['password'], password):
                user = User(user_data)
                login_user(user)
                flash(f'Welcome back, {user.first_name or user.username}!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password.', 'error')
        else:
            flash('Please enter both username and password.', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        errors = []

        if not username:
            errors.append('Username is required.')
        elif len(username) < 3:
            errors.append('Username must be at least 3 characters long.')
        elif db.users.find_one({'username': username}):
            errors.append('Username already exists.')

        if not email:
            errors.append('Email is required.')
        elif db.users.find_one({'email': email}):
            errors.append('Email already exists.')

        if not first_name:
            errors.append('First name is required.')

        if not password:
            errors.append('Password is required.')
        elif len(password) < 6:
            errors.append('Password must be at least 6 characters long.')

        if password != confirm_password:
            errors.append('Passwords do not match.')

        if errors:
            for error in errors:
                flash(error, 'error')
        else:
            # Create user
            try:
                user_data = {
                    'username': username,
                    'email': email,
                    'password': generate_password_hash(password),
                    'first_name': first_name,
                    'last_name': last_name
                }
                result = db.users.insert_one(user_data)
                user_data['_id'] = result.inserted_id

                flash(f'Account created successfully! Welcome, {first_name}!', 'success')

                # Auto-login the user
                user = User(user_data)
                login_user(user)
                return redirect(url_for('index'))

            except Exception as e:
                flash('An error occurred while creating your account. Please try again.', 'error')

    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/database')
@login_required
def view_database():
    diseases = list(db.diseases.find())
    return render_template('database.html', diseases=diseases)

@app.route('/search', methods=['POST'])
@login_required
def search():
    disease_input = request.json.get('disease', '').lower()

    # MongoDB query with case-insensitive search
    disease = db.diseases.find_one(
        {"name": {"$regex": f".*{disease_input}.*", "$options": "i"}}
    )

    if not disease:
        return jsonify({"error": "Disease not found"}), 404

    # Organize solutions by type with enhanced data
    solutions = {"organic": [], "inorganic": []}
    for solution in disease.get('solutions', []):
        solution_data = {
            "solution": solution['solution'],
            "image": solution.get('image', ''),
            "effectiveness": solution.get('effectiveness', 'Unknown'),
            "application": solution.get('application', 'Follow standard guidelines')
        }
        solutions[solution['type']].append(solution_data)

    return jsonify({
        "disease": disease['name'],
        "description": disease.get('description', ''),
        "image": disease.get('image', ''),
        "solutions": solutions
    })

@app.route('/reset-db', methods=['POST'])
def reset_database():
    """Reset database with new image data structure"""
    try:
        # Drop existing collections
        db.diseases.drop()
        db.solutions.drop()

        # Reinitialize with new data
        init_db()

        return jsonify({"message": "Database reset successfully with image support!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)