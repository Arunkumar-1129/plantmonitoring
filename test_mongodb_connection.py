#!/usr/bin/env python3
"""
MongoDB Connection Test for PlantDoc Project
This script verifies the MongoDB connection and shows what data will be visible in MongoDB Compass
"""

from pymongo import MongoClient
import json
from datetime import datetime

def test_mongodb_connection():
    """Test MongoDB connection and display database information"""
    
    print("🧭 MongoDB Compass Connection Test for PlantDoc")
    print("=" * 60)
    
    try:
        # Connect to MongoDB (same connection as your Django app)
        client = MongoClient('mongodb://localhost:27017/')
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB Connection: SUCCESSFUL")
        
        # Get database
        db = client['plant_diseases']
        print(f"📊 Database: {db.name}")
        
        # Get collections
        collections = db.list_collection_names()
        print(f"📁 Collections: {collections}")
        
        if 'diseases' in collections:
            diseases_collection = db.diseases
            
            # Get collection stats
            total_docs = diseases_collection.count_documents({})
            print(f"📄 Total Documents: {total_docs}")
            
            # Show sample documents
            print("\n🌿 Sample Plant Diseases in Database:")
            print("-" * 40)
            
            sample_diseases = list(diseases_collection.find({}).limit(5))
            
            for i, disease in enumerate(sample_diseases, 1):
                print(f"\n{i}. Disease: {disease['name'].title()}")
                print(f"   Description: {disease['description'][:80]}...")
                print(f"   Solutions: {len(disease.get('solutions', []))} treatments")
                
                # Show solution types
                organic_count = len([s for s in disease.get('solutions', []) if s.get('type') == 'organic'])
                inorganic_count = len([s for s in disease.get('solutions', []) if s.get('type') == 'inorganic'])
                print(f"   - Organic: {organic_count}, Chemical: {inorganic_count}")
            
            # Show database schema
            print(f"\n📋 Database Schema Preview:")
            print("-" * 30)
            if sample_diseases:
                sample_doc = sample_diseases[0]
                print("Document Structure:")
                print(f"  _id: ObjectId (MongoDB unique identifier)")
                print(f"  name: String ('{sample_doc['name']}')")
                print(f"  description: String (disease description)")
                print(f"  solutions: Array of Objects")
                print(f"    - type: String ('organic' or 'inorganic')")
                print(f"    - solution: String (treatment description)")
                print(f"    - effectiveness: String (High/Medium/Low)")
                print(f"    - application: String (instructions)")
        
        else:
            print("⚠️  No 'diseases' collection found. Run the Django app to create data.")
        
        # Connection information for MongoDB Compass
        print(f"\n🧭 MongoDB Compass Connection Details:")
        print("-" * 40)
        print(f"Connection String: mongodb://localhost:27017")
        print(f"Host: localhost")
        print(f"Port: 27017")
        print(f"Database: plant_diseases")
        print(f"Collection: diseases")
        print(f"Authentication: None (local connection)")
        
        # Show what you'll see in Compass
        print(f"\n👀 What You'll See in MongoDB Compass:")
        print("-" * 40)
        print(f"• Database 'plant_diseases' in the left sidebar")
        print(f"• Collection 'diseases' with {total_docs if 'diseases' in collections else 0} documents")
        print(f"• Each document representing a plant disease")
        print(f"• Visual schema showing document structure")
        print(f"• Query interface for searching diseases")
        print(f"• Real-time updates when Django app modifies data")
        
        client.close()
        
    except Exception as e:
        print(f"❌ MongoDB Connection Failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure MongoDB service is running")
        print("2. Check if port 27017 is available")
        print("3. Verify MongoDB is installed correctly")
        return False
    
    return True

def show_compass_instructions():
    """Show step-by-step MongoDB Compass connection instructions"""
    
    print(f"\n🚀 MongoDB Compass Connection Steps:")
    print("=" * 50)
    print("1. Download MongoDB Compass from: https://www.mongodb.com/products/compass")
    print("2. Install and launch MongoDB Compass")
    print("3. Click 'New Connection'")
    print("4. Enter connection string: mongodb://localhost:27017")
    print("5. Click 'Connect'")
    print("6. Navigate to 'plant_diseases' database")
    print("7. Click on 'diseases' collection")
    print("8. Explore your plant disease data!")
    
    print(f"\n💡 Pro Tips:")
    print("• Use the filter bar to search for specific diseases")
    print("• Click on documents to view detailed information")
    print("• Use the Schema tab to understand data structure")
    print("• Try queries like: {\"name\": \"powdery mildew\"}")
    print("• Export data using the Export button")

if __name__ == "__main__":
    print(f"🕐 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if test_mongodb_connection():
        show_compass_instructions()
        print(f"\n🎉 Your PlantDoc database is ready for MongoDB Compass!")
    else:
        print(f"\n❌ Please fix MongoDB connection issues before using Compass.")
    
    print(f"\n📱 Your Django App URLs:")
    print("• Main App: http://127.0.0.1:8000/")
    print("• Database View: http://127.0.0.1:8000/database/")
    print("• Reset Database: http://127.0.0.1:8000/reset-db/")
