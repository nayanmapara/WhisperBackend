from flask import Flask, jsonify, request, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

from scraping.scraper import scrape_links

from pymongo import MongoClient, errors as PyMongoError

from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enable CORS
CORS(app)

# Set up MongoDB connection
host = os.environ["DB_HOST"]
password = os.environ["DB_PASS"]
db_name = os.environ["DB_NAME"]
db_collection = os.environ["DB_COLLECTION"]
mongodb_uri = f"mongodb+srv://{host}:{password}@cluster0.gurdfx8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(mongodb_uri)
db = client[db_name]

collection = db[db_collection]

# Set up rate limiter
limiter = Limiter(
    get_remote_address,
    app=app
)

@app.route('/')
def index():
    return 'Welcome to WhisperBackend!'

@app.route('/api/scrape')
@limiter.limit("10 per month")
def scrape():
    return jsonify(scrape_links())

@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    data = request.json
    email = data.get('email')
    option = data.get('option')
    
    if not email or not option:
        return jsonify({'error': 'Email and option are required'}), 400
    
    try:
        # Check if the email already exists in the database
        existing_subscriber = collection.find_one({'email': email})
        
        if existing_subscriber:
            if existing_subscriber['option'] == option:
                return jsonify({'message': 'Already subscribed'}), 200
            else:
                # Update the option and last_changed for the existing email
                result = collection.update_one(
                    {'email': email},
                    {
                        '$set': {'option': option, 'last_changed': datetime.utcnow()}
                    }
                )
                
                if result.modified_count > 0:
                    return jsonify({'message': 'Updated'}), 200
                else:
                    return jsonify({'error': 'Failed to update subscription'}), 500
        else:
            result = collection.insert_one({
                'email': email,
                'option': option,
                'created': datetime.utcnow(),
                'last_changed': datetime.utcnow()
            })
            
            if result.inserted_id:
                return jsonify({'message': 'Success', 'id': str(result.inserted_id)}), 201
            else:
                return jsonify({'error': 'Failed'}), 500
                
    except PyMongoError as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/dashboard')
def dashboard():
    total_subscriptions = collection.count_documents({})
    new_subscriptions = collection.count_documents({'created': {'$gte': datetime.utcnow() - timedelta(days=30)}})
    
    return render_template('dashboard.html', 
                           total_subscriptions=total_subscriptions, 
                           new_subscriptions=new_subscriptions)


if __name__ == '__main__':
    app.run(debug=True)
