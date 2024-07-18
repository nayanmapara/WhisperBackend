import logging
from flask import Flask, jsonify, request, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import bcrypt

try:
    from .scraping.scraper import scrape_links
    from .emailing.mail import send_email
except ImportError:
    from scraping.scraper import scrape_links
    from emailing.mail import send_email

from pymongo import MongoClient, errors as PyMongoError
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enable CORS
CORS(app)

# Set up MongoDB connection
db_name = os.environ["DB_NAME"]
db_collection = os.environ["DB_COLLECTION"]
user_collection = os.environ["USER_COLLECTION"] 
mongodb_uri = os.environ["MONGODB_URI"]

# Define SMTP configuration
smtp_config = {
    'host': os.environ["SMTP_HOST"],
    'port': int(os.environ["SMTP_PORT"]),
    'user': os.environ["SMTP_USER"],
    'password': os.environ["SMTP_PASSWORD"]
}

client = MongoClient(mongodb_uri)
db = client[db_name]
collection = db[db_collection]
users = db[user_collection]

# Set up rate limiter
limiter = Limiter(
    get_remote_address,
    app=app
)

# Set up JWT manager
app.config['JWT_SECRET_KEY'] = os.environ["JWT_SECRET_KEY"]
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=30)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
jwt = JWTManager(app)

@app.route('/')
def index():
    return 'Welcome to WhisperBackend!'

@app.route('/api/login', methods=['POST'])
def login():
    """
    Login endpoint to authenticate user and provide JWT token.
    """
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({"msg": "Username and password are required"}), 400

    # Fetch user data from the database
    user = users.find_one({'username': username})
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        access_token = create_access_token(identity=username)
        return jsonify(login=True, access_token=access_token), 200

    return jsonify(login=False), 401

@app.route('/api/scrape')
@jwt_required()
@limiter.limit("10 per month")
def scrape():
    """
    Scrape links from the web and return the results.
    """
    return jsonify(scrape_links())

@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    """
    Subscribe an email to receive emails of a specified type. (e.g., 'Student' or 'WorkPermit')
    """

    data = request.json
    email = data.get('email')
    option = data.get('option')
    
    if not email or not option:
        logger.warning("Email and option are required for subscription")
        return jsonify({'error': 'Email and option are required'}), 400
    
    try:
        # Check if the email already exists in the database
        existing_subscriber = collection.find_one({'email': email})
        
        if existing_subscriber:
            if existing_subscriber['option'] == option:
                logger.info(f"Email {email} is already subscribed with option {option}")
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
                    logger.info(f"Updated subscription for email {email} to option {option}")
                    return jsonify({'message': 'Updated'}), 200
                else:
                    logger.error(f"Failed to update subscription for email {email}")
                    return jsonify({'error': 'Failed to update subscription'}), 500
        else:
            result = collection.insert_one({
                'email': email,
                'option': option,
                'created': datetime.utcnow(),
                'last_changed': datetime.utcnow()
            })
            
            if result.inserted_id:
                logger.info(f"Successfully subscribed email {email} with option {option}")
                return jsonify({'message': 'Success', 'id': str(result.inserted_id)}), 201
            else:
                logger.error(f"Failed to subscribe email {email}")
                return jsonify({'error': 'Failed'}), 500
                
    except PyMongoError as e:
        logger.error(f"MongoDB error during subscription for email {email}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/send_emails', methods=['POST'])
@jwt_required()
def send_emails():
    """
    Send emails to all recipients based on the specified type (e.g., 'Student' or 'WorkPermit') provided in the request body. Each type will have its own subject and HTML content.
    """

    data_list = request.json

    if not isinstance(data_list, list):
        logger.warning("Request data should be a list of email data")
        return jsonify({'error': 'Request data should be a list of email data'}), 400

    for data in data_list:
        email_type = data.get('type')  # 'Student' or 'WorkPermit'
        email_data = data.get('email_data')  # JSON with HTML content and subject

        if not email_type or not email_data:
            logger.warning("Email type and email data are required for sending emails")
            return jsonify({'error': 'Email type and email data are required'}), 400

        subject = email_data.get('subject')
        html_content = email_data.get('html_content')

        if not subject or not html_content:
            logger.warning("Subject and HTML content are required for sending emails")
            return jsonify({'error': 'Subject and HTML content are required'}), 400

        # Fetch email addresses from MongoDB based on type
        recipients = collection.find({'option': email_type}, {'email': 1, '_id': 0})
        recipient_emails = [recipient['email'] for recipient in recipients]

        if not recipient_emails:
            logger.info(f"No recipients found for the specified type: {email_type}")
            continue  # Skip to the next data item

        # Send emails
        for email in recipient_emails:
            success = send_email(smtp_config, email, subject, html_content)
            if not success:
                logger.error(f"Failed to send email to: {email}")

        logger.info(f"Emails sent successfully to all recipients of type {email_type}")

    return jsonify({'message': 'Emails sent successfully to all specified types'}), 200

@app.route('/api/unsubscribe', methods=['POST'])
def unsubscribe():
    """
    Unsubscribe an email from receiving further emails.
    """

    data = request.json
    email = data.get('email')
    
    if not email:
        logger.warning("Email is required for unsubscription")
        return jsonify({'error': 'Email is required'}), 400
    
    try:
        # Remove the email from the database
        result = collection.delete_one({'email': email})
        
        if result.deleted_count > 0:
            logger.info(f"Unsubscribed email {email} successfully")
            return jsonify({'message': 'Unsubscribed successfully'}), 200
        else:
            logger.info(f"Email {email} not found for unsubscription")
            return jsonify({'error': 'Email not found'}), 404
                
    except PyMongoError as e:
        logger.error(f"MongoDB error during unsubscription for email {email}: {e}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_metrics():
    """
    Retrieve dashboard metrics.
    
    Returns:
        JSON response with total and new subscription counts.
    """
    try:
        total_subscriptions_count = collection.count_documents({})
        new_subscriptions_count = collection.count_documents({'created': {'$gte': datetime.utcnow() - timedelta(days=30)}})
        
        logger.info("Dashboard metrics retrieved successfully")
        
        response = {
            'total_subscriptions': total_subscriptions_count,
            'new_subscriptions_last_30_days': new_subscriptions_count
        }
        
        return jsonify(response), 200

    except PyMongoError as e:
        logger.error(f"Error retrieving dashboard metrics: {e}")
        return jsonify({'error': 'Error retrieving dashboard metrics'}), 500


if __name__ == '__main__':
    app.run(debug=True)