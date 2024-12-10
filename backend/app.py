from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
from config import Config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

def init_db():
    """Initialize the SQLite database with our required tables"""
    try:
        with sqlite3.connect(Config.DATABASE_NAME) as conn:
            c = conn.cursor()
            # Table for storing code -> phone number mappings
            c.execute('''
                CREATE TABLE IF NOT EXISTS mappings
                (code TEXT PRIMARY KEY, 
                phone_number TEXT, 
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP)
            ''')
            # Table for storing message history
            c.execute('''
                CREATE TABLE IF NOT EXISTS messages
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                code TEXT,
                phone_number TEXT,
                message TEXT,
                status TEXT,
                error_message TEXT)
            ''')
            conn.commit()
            logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

def send_sms(phone_number, message):
    """Send SMS via Twilio or simulate in test mode"""
    if Config.TEST_MODE:
        logger.info(f"TEST MODE: Would send '{message}' to {phone_number}")
        return True, "Test message simulated"
    
    # This will be replaced with actual Twilio code
    try:
        # Placeholder for Twilio implementation
        return True, "Message sent"
    except Exception as e:
        return False, str(e)

@app.route('/api/mapping', methods=['POST'])
def add_mapping():
    """Add a new code -> phone number mapping"""
    data = request.json
    code = data.get('code')
    phone = data.get('phone')
    
    if not code or not phone:
        return jsonify({"error": "Missing code or phone number"}), 400
        
    if len(code) != 6:
        return jsonify({"error": "Code must be 6 digits"}), 400
    
    try:
        with sqlite3.connect(Config.DATABASE_NAME) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT OR REPLACE INTO mappings (code, phone_number)
                VALUES (?, ?)
            ''', (code, phone))
            conn.commit()
        logger.info(f"Added mapping: {code} -> {phone}")
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"Error adding mapping: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/mappings', methods=['GET'])
def get_mappings():
    """Get all existing code -> phone number mappings"""
    try:
        with sqlite3.connect(Config.DATABASE_NAME) as conn:
            c = conn.cursor()
            c.execute('SELECT code, phone_number FROM mappings ORDER BY created_at DESC')
            mappings = dict(c.fetchall())
            return jsonify(mappings)
    except Exception as e:
        logger.error(f"Error fetching mappings: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/send-message', methods=['POST'])
def send_message():
    """Send an SMS message to the phone number mapped to the given code"""
    data = request.json
    code = data.get('code')
    message = data.get('message')
    
    if not code or not message:
        return jsonify({"error": "Missing code or message"}), 400
    
    try:
        with sqlite3.connect(Config.DATABASE_NAME) as conn:
            c = conn.cursor()
            c.execute('SELECT phone_number FROM mappings WHERE code = ?', (code,))
            result = c.fetchone()
            
            if not result:
                return jsonify({"error": "Code not found"}), 404
                
            phone_number = result[0]
            
            # Send message (or simulate in test mode)
            success, status_message = send_sms(phone_number, message)
            
            # Record attempt in database
            c.execute('''
                INSERT INTO messages 
                (code, phone_number, message, status, error_message)
                VALUES (?, ?, ?, ?, ?)
            ''', (code, phone_number, message, 
                 'sent' if success else 'failed', 
                 None if success else status_message))
            conn.commit()
            
            if success:
                return jsonify({
                    "status": "success",
                    "phone": phone_number
                })
            else:
                return jsonify({
                    "error": "Failed to send message",
                    "details": status_message
                }), 500
                
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status and configuration"""
    return jsonify({
        "test_mode": Config.TEST_MODE,
        "twilio_configured": bool(Config.TWILIO_ACCOUNT_SID and 
                                Config.TWILIO_AUTH_TOKEN and 
                                Config.TWILIO_PHONE_NUMBER),
        "database": Config.DATABASE_NAME
    })

if __name__ == '__main__':
    init_db()
    logger.info(f"Starting server in {'TEST' if Config.TEST_MODE else 'PRODUCTION'} mode")
    app.run(debug=True, port=5000)