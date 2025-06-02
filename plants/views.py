from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import json
from pymongo import MongoClient
import logging

# MongoDB connection
logger = logging.getLogger(__name__)

try:
    client = MongoClient('mongodb://localhost:27017/')
    client.admin.command('ping')
    logger.info("✅ Successfully connected to MongoDB!")
    db = client['plant_diseases']
except Exception as e:
    logger.error(f"❌ MongoDB connection failed: {e}")
    db = None

def login_view(request):
    """Render the login page"""
    if request.user.is_authenticated:
        return redirect('plants:index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                return redirect('plants:index')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please enter both username and password.')

    return render(request, 'plants/login.html')

def signup_view(request):
    """Render the signup page"""
    if request.user.is_authenticated:
        return redirect('plants:index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Validation
        errors = []

        if not username:
            errors.append('Username is required.')
        elif len(username) < 3:
            errors.append('Username must be at least 3 characters long.')
        elif User.objects.filter(username=username).exists():
            errors.append('Username already exists.')

        if not email:
            errors.append('Email is required.')
        else:
            try:
                validate_email(email)
                if User.objects.filter(email=email).exists():
                    errors.append('Email already exists.')
            except ValidationError:
                errors.append('Please enter a valid email address.')

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
                messages.error(request, error)
        else:
            # Create user
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                messages.success(request, f'Account created successfully! Welcome, {first_name}!')

                # Auto-login the user
                user = authenticate(request, username=username, password=password)
                if user:
                    login(request, user)
                    return redirect('plants:index')
                else:
                    return redirect('plants:login')

            except Exception as e:
                messages.error(request, 'An error occurred while creating your account. Please try again.')

    return render(request, 'plants/signup.html')

def logout_view(request):
    """Logout user"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('plants:login')

@login_required
def index(request):
    """Render the main page"""
    return render(request, 'plants/index.html')

@login_required
def view_database(request):
    """View MongoDB database content"""
    try:
        if db is None:
            return JsonResponse({"error": "Database connection failed"}, status=500)

        # Get all diseases from MongoDB
        diseases = list(db.diseases.find({}))

        # Convert ObjectId to string and rename for template compatibility
        for disease in diseases:
            if '_id' in disease:
                disease['id'] = str(disease['_id'])
                del disease['_id']

        context = {
            'diseases': diseases,
            'total_diseases': len(diseases),
            'database_name': 'plant_diseases',
            'collection_name': 'diseases'
        }

        return render(request, 'plants/database.html', context)

    except Exception as e:
        context = {
            'error': str(e),
            'diseases': [],
            'total_diseases': 0,
            'database_name': 'plant_diseases',
            'collection_name': 'diseases'
        }
        return render(request, 'plants/database.html', context)



@csrf_exempt
@require_http_methods(["POST"])
def search_disease(request):
    """Search for disease solutions"""
    try:
        if db is None:
            return JsonResponse({"error": "Database connection failed"}, status=500)

        data = json.loads(request.body)
        disease_input = data.get('disease', '').lower()

        if not disease_input:
            return JsonResponse({"error": "Please enter a disease name"}, status=400)

        # Search for disease (case-insensitive) using MongoDB
        disease = db.diseases.find_one(
            {"name": {"$regex": f".*{disease_input}.*", "$options": "i"}}
        )

        if not disease:
            return JsonResponse({"error": "Disease not found"}, status=404)

        # Organize solutions by type
        solutions = {"organic": [], "inorganic": []}
        for solution in disease.get('solutions', []):
            solution_data = {
                "solution": solution['solution'],
                "effectiveness": solution.get('effectiveness', 'Unknown'),
                "application": solution.get('application', 'Follow standard guidelines')
            }
            solutions[solution['type']].append(solution_data)

        return JsonResponse({
            "disease": disease['name'],
            "description": disease.get('description', ''),
            "solutions": solutions
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def reset_database(request):
    """Reset database with sample data"""
    try:
        if db is None:
            return JsonResponse({"error": "Database connection failed"}, status=500)

        # Clear existing data
        db.diseases.drop()

        # Sample data - text only, no images
        sample_diseases = [
            {
                "name": "powdery mildew",
                "description": "A fungal disease that appears as white powdery coating on leaves and stems",
                "solutions": [
                    {
                        "type": "organic",
                        "solution": "Baking soda spray (1 tbsp per gallon water)",
                        "effectiveness": "High",
                        "application": "Spray weekly on affected areas"
                    },
                    {
                        "type": "organic",
                        "solution": "Neem oil treatment",
                        "effectiveness": "High",
                        "application": "Apply every 7-14 days"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Sulfur-based fungicide",
                        "effectiveness": "Very High",
                        "application": "Apply as directed on label"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Systemic fungicide (myclobutanil)",
                        "effectiveness": "Very High",
                        "application": "Professional application recommended"
                    }
                ]
            },
            {
                "name": "blight",
                "description": "A plant disease causing brown spots and wilting of leaves and stems",
                "solutions": [
                    {
                        "type": "organic",
                        "solution": "Copper sulfate spray",
                        "effectiveness": "High",
                        "application": "Apply every 7-10 days in dry weather"
                    },
                    {
                        "type": "organic",
                        "solution": "Bacillus subtilis biological control",
                        "effectiveness": "Medium",
                        "application": "Apply as preventive treatment"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Chlorothalonil fungicide",
                        "effectiveness": "Very High",
                        "application": "Apply every 7-14 days"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Mancozeb fungicide",
                        "effectiveness": "Very High",
                        "application": "Use with protective equipment"
                    }
                ]
            },
            {
                "name": "rust",
                "description": "A fungal disease causing orange-red pustules on leaf undersides",
                "solutions": [
                    {
                        "type": "organic",
                        "solution": "Sulfur dust application",
                        "effectiveness": "High",
                        "application": "Apply early morning when dew is present"
                    },
                    {
                        "type": "organic",
                        "solution": "Neem oil spray treatment",
                        "effectiveness": "Medium",
                        "application": "Apply in cool weather, avoid hot sun"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Propiconazole systemic fungicide",
                        "effectiveness": "Very High",
                        "application": "Apply at first sign of disease"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Tebuconazole for severe cases",
                        "effectiveness": "Very High",
                        "application": "Professional application only"
                    }
                ]
            },
            {
                "name": "aphid infestation",
                "description": "Small green or black insects clustering on stems and leaves",
                "solutions": [
                    {
                        "type": "organic",
                        "solution": "Insecticidal soap spray",
                        "effectiveness": "High",
                        "application": "Spray every 2-3 days until controlled"
                    },
                    {
                        "type": "organic",
                        "solution": "Ladybug biological control",
                        "effectiveness": "Very High",
                        "application": "Release 1500 per garden in evening"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Imidacloprid systemic insecticide",
                        "effectiveness": "Very High",
                        "application": "Soil drench or foliar spray"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Pyrethrin contact spray",
                        "effectiveness": "High",
                        "application": "Apply in early morning or evening"
                    }
                ]
            },
            {
                "name": "black spot",
                "description": "Fungal disease causing black spots on leaves, common in roses",
                "solutions": [
                    {
                        "type": "organic",
                        "solution": "Baking soda and oil spray",
                        "effectiveness": "Medium",
                        "application": "Spray weekly during growing season"
                    },
                    {
                        "type": "organic",
                        "solution": "Copper fungicide spray",
                        "effectiveness": "High",
                        "application": "Apply every 7-14 days"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Trifloxystrobin fungicide",
                        "effectiveness": "Very High",
                        "application": "Apply at first sign of disease"
                    }
                ]
            },
            {
                "name": "downy mildew",
                "description": "Fungal disease causing yellow patches and fuzzy growth on leaf undersides",
                "solutions": [
                    {
                        "type": "organic",
                        "solution": "Improve air circulation and reduce humidity",
                        "effectiveness": "Medium",
                        "application": "Space plants properly, prune for airflow"
                    },
                    {
                        "type": "organic",
                        "solution": "Copper hydroxide spray",
                        "effectiveness": "High",
                        "application": "Apply in early morning"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Metalaxyl systemic fungicide",
                        "effectiveness": "Very High",
                        "application": "Soil drench and foliar spray"
                    }
                ]
            },
            {
                "name": "spider mites",
                "description": "Tiny pests causing stippled leaves and fine webbing",
                "solutions": [
                    {
                        "type": "organic",
                        "solution": "Predatory mites release",
                        "effectiveness": "Very High",
                        "application": "Release when mites first detected"
                    },
                    {
                        "type": "organic",
                        "solution": "Neem oil and water spray",
                        "effectiveness": "High",
                        "application": "Spray undersides of leaves weekly"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Abamectin miticide",
                        "effectiveness": "Very High",
                        "application": "Apply with spreader-sticker"
                    }
                ]
            },
            {
                "name": "leaf spot",
                "description": "Fungal or bacterial disease causing circular spots on leaves",
                "solutions": [
                    {
                        "type": "organic",
                        "solution": "Remove affected leaves and improve air circulation",
                        "effectiveness": "Medium",
                        "application": "Prune infected parts and dispose properly"
                    },
                    {
                        "type": "organic",
                        "solution": "Copper-based organic fungicide",
                        "effectiveness": "High",
                        "application": "Apply every 10-14 days"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Chlorothalonil fungicide spray",
                        "effectiveness": "Very High",
                        "application": "Apply according to label directions"
                    }
                ]
            },
            {
                "name": "anthracnose",
                "description": "Fungal disease causing dark, sunken lesions on leaves and fruits",
                "solutions": [
                    {
                        "type": "organic",
                        "solution": "Copper sulfate spray treatment",
                        "effectiveness": "High",
                        "application": "Apply during cool, wet weather"
                    },
                    {
                        "type": "organic",
                        "solution": "Bacillus subtilis biological fungicide",
                        "effectiveness": "Medium",
                        "application": "Apply as preventive treatment"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Azoxystrobin systemic fungicide",
                        "effectiveness": "Very High",
                        "application": "Apply at first sign of disease"
                    }
                ]
            },
            {
                "name": "fusarium wilt",
                "description": "Soil-borne fungal disease causing yellowing and wilting of plants",
                "solutions": [
                    {
                        "type": "organic",
                        "solution": "Soil solarization and crop rotation",
                        "effectiveness": "Medium",
                        "application": "Cover soil with plastic for 6-8 weeks in summer"
                    },
                    {
                        "type": "organic",
                        "solution": "Trichoderma biological control",
                        "effectiveness": "High",
                        "application": "Apply to soil before planting"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Benomyl systemic fungicide",
                        "effectiveness": "High",
                        "application": "Soil drench treatment"
                    }
                ]
            },
            {
                "name": "bacterial canker",
                "description": "Bacterial infection causing sunken, dark lesions on stems and branches",
                "solutions": [
                    {
                        "type": "organic",
                        "solution": "Copper hydroxide spray",
                        "effectiveness": "High",
                        "application": "Apply during dormant season"
                    },
                    {
                        "type": "organic",
                        "solution": "Prune infected branches and sterilize tools",
                        "effectiveness": "Medium",
                        "application": "Cut 6 inches below infected area"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Streptomycin antibiotic spray",
                        "effectiveness": "Very High",
                        "application": "Apply during bloom period"
                    }
                ]
            },
            {
                "name": "scale insects",
                "description": "Small, hard-shelled insects that attach to stems and leaves",
                "solutions": [
                    {
                        "type": "organic",
                        "solution": "Horticultural oil spray",
                        "effectiveness": "High",
                        "application": "Apply during dormant season"
                    },
                    {
                        "type": "organic",
                        "solution": "Beneficial parasitic wasps release",
                        "effectiveness": "Very High",
                        "application": "Release when scales are detected"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Systemic insecticide (imidacloprid)",
                        "effectiveness": "Very High",
                        "application": "Soil application in spring"
                    }
                ]
            },
            {
                "name": "thrips",
                "description": "Tiny insects causing silvery streaks and black spots on leaves",
                "solutions": [
                    {
                        "type": "organic",
                        "solution": "Blue sticky traps",
                        "effectiveness": "Medium",
                        "application": "Place traps around affected plants"
                    },
                    {
                        "type": "organic",
                        "solution": "Predatory mites (Amblyseius cucumeris)",
                        "effectiveness": "High",
                        "application": "Release in greenhouse or garden"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Spinosad insecticide spray",
                        "effectiveness": "Very High",
                        "application": "Apply in evening to avoid bee exposure"
                    }
                ]
            },
            {
                "name": "whitefly",
                "description": "Small white flying insects that cluster on leaf undersides",
                "solutions": [
                    {
                        "type": "organic",
                        "solution": "Yellow sticky traps",
                        "effectiveness": "Medium",
                        "application": "Place traps near affected plants"
                    },
                    {
                        "type": "organic",
                        "solution": "Encarsia formosa parasitic wasp",
                        "effectiveness": "Very High",
                        "application": "Release in greenhouse environments"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Acetamiprid systemic insecticide",
                        "effectiveness": "Very High",
                        "application": "Apply as soil drench or foliar spray"
                    }
                ]
            },
            {
                "name": "root rot",
                "description": "Fungal disease affecting plant roots, causing yellowing and wilting",
                "solutions": [
                    {
                        "type": "organic",
                        "solution": "Improve drainage and reduce watering",
                        "effectiveness": "High",
                        "application": "Ensure proper soil drainage"
                    },
                    {
                        "type": "organic",
                        "solution": "Mycorrhizal fungi inoculant",
                        "effectiveness": "Medium",
                        "application": "Apply to soil around roots"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Metalaxyl fungicide soil drench",
                        "effectiveness": "Very High",
                        "application": "Apply to soil around affected plants"
                    }
                ]
            },
            {
                "name": "fire blight",
                "description": "Bacterial disease causing blackened, burnt appearance in branches",
                "solutions": [
                    {
                        "type": "organic",
                        "solution": "Prune infected branches during dry weather",
                        "effectiveness": "High",
                        "application": "Cut 12 inches below infected area"
                    },
                    {
                        "type": "organic",
                        "solution": "Copper sulfate spray",
                        "effectiveness": "Medium",
                        "application": "Apply during dormant season"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Streptomycin antibiotic spray",
                        "effectiveness": "Very High",
                        "application": "Apply during bloom period"
                    }
                ]
            },
            {
                "name": "mosaic virus",
                "description": "Viral disease causing mottled yellow and green patterns on leaves",
                "solutions": [
                    {
                        "type": "organic",
                        "solution": "Remove infected plants immediately",
                        "effectiveness": "High",
                        "application": "Destroy infected plants to prevent spread"
                    },
                    {
                        "type": "organic",
                        "solution": "Control aphid vectors with beneficial insects",
                        "effectiveness": "Medium",
                        "application": "Release ladybugs and lacewings"
                    },
                    {
                        "type": "inorganic",
                        "solution": "No chemical cure - focus on prevention",
                        "effectiveness": "Low",
                        "application": "Use virus-resistant plant varieties"
                    }
                ]
            },
            {
                "name": "clubroot",
                "description": "Soil-borne disease causing swollen, distorted roots in brassicas",
                "solutions": [
                    {
                        "type": "organic",
                        "solution": "Lime application to raise soil pH",
                        "effectiveness": "High",
                        "application": "Apply lime to achieve pH 7.2 or higher"
                    },
                    {
                        "type": "organic",
                        "solution": "Long crop rotation (7+ years)",
                        "effectiveness": "Very High",
                        "application": "Avoid brassicas for 7-10 years"
                    },
                    {
                        "type": "inorganic",
                        "solution": "Fluazinam fungicide soil treatment",
                        "effectiveness": "High",
                        "application": "Apply before planting susceptible crops"
                    }
                ]
            }
        ]

        # Insert data into MongoDB
        db.diseases.insert_many(sample_diseases)

        return JsonResponse({"message": "Database reset successfully with Django and MongoDB!"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
