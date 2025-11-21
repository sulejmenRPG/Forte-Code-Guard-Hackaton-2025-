# Database configuration
DB_PASSWORD = "admin123"
API_KEY = "hardcoded_key_12345"
SECRET_TOKEN = "my_secret_token"

def get_connection():
    # SQL injection vulnerability
    query = "SELECT * FROM users WHERE id = " + user_id 
