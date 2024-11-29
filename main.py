from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)
import bcrypt
import sqlite3
from models import create_table,execute_query
from bot import ask
import config
from utils import role_required


# Flask app setup
app = Flask(__name__)
DATABASE = config.DATABASE
SECRET_KEY = config.SECRET_KEY
app.config['SECRET_KEY'] = SECRET_KEY
jwt = JWTManager(app)


# Routes

# Endpoint for user registration
@app.route('/register', methods=['POST'])
def register_user():
    """
    User Registration Endpoint:
    
    This endpoint allows new users to register by providing a username, password, and name.
    The role is optional and defaults to 'User ' (role 2). The following steps are performed:
    
    1. The request data is retrieved from the JSON body.
    2. Input validation is performed to ensure that the username, password, and name are provided.
    3. A check is made to see if the username already exists in the database. If it does, a 400 response is returned.
    4. The password is hashed using bcrypt for security before storing it in the database.
    5. The new user is inserted into the `user_details` table. If an error occurs during insertion, a 500 response is returned.
    6. If registration is successful, a 200 response with a success message is returned.
    
    Returns:
        - 200: User created successfully.
        - 400: Missing required fields or username already taken.
        - 500: Error creating user.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    role = data.get('role', 2)  # Default role is 'User'

    # Validate input data
    if not username or not password or not name:
        return jsonify({'message': 'Missing username, password, or name'}), 400

    existing_user = execute_query(
        'SELECT id FROM user_details WHERE username = ?', (username,), fetch_one=True
    )
    # Check if the username is already taken
    if existing_user:
        return jsonify({'message': 'Username already taken'}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        # Insert new user into the database
        execute_query(
            'INSERT INTO user_details (role, username, password, name) VALUES (?, ?, ?, ?)',
            (role, username, hashed_password, name),
            commit=True
        )
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Error creating user'}), 500

    return jsonify({'message': 'User created successfully'}), 200


# Endpoint for user login
@app.route('/login', methods=['POST'])
def login_user():
    """
    User Login Endpoint:
    
    This endpoint allows existing users to log in by providing their username and password. 
    The following steps are performed:
    
    1. The request data is retrieved from the JSON body.
    2. Input validation is performed to ensure that both username and password are provided.
    3. The user is fetched from the database based on the provided username.
    4. If the user exists, the provided password is checked against the stored hashed password.
    5. If the credentials are valid, an access token is generated for the user, and user details are returned in the response.
    6. If the credentials are invalid, a 401 response is returned.
    
    Returns:
        - 200: Logged in successfully with user details and access token.
        - 400: Missing username or password.
        - 401: Invalid credentials.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    # Fetch user details from the database
    user = execute_query(
        'SELECT * FROM user_details WHERE username = ?', (username,), fetch_one=True
    )
    # Check if the user exists and if the password matches
    if user and bcrypt.checkpw(password.encode('utf-8'),user[3].encode('utf-8')):
        # Create access token for the user
        access_token = create_access_token(identity=str(user[0]))
        username = user[2]
        role = user[1]
        name = user[4]
        karma = user[5]
        return jsonify({'message': f'Logged in!','username':username,'name':name,'role':role,'karma':karma, 'access_token': access_token}), 200

    return jsonify({'message': 'Invalid credentials'}), 401



# Secure endpoint for chat functionality
@app.route('/chat', methods=['POST'])
@jwt_required()
@role_required([0,1]) # Restrict access to admins and moderators
def secure_resource():
    """
    Chat Functionality Endpoint:
    
    This endpoint allows authenticated users with admin or moderator roles to perform chat-related queries.
    The following steps are performed:
    
    1. The current user's ID is retrieved from the JWT token.
    2. The user's name is fetched from the database based on the ID.
    3. The request data is retrieved from the JSON body, and the 'query' field is validated.
    4. The query is processed using an external bot function, and the resulting SQL query is executed.
    5. The response, including the current user's name, the executed SQL query, and the result, is returned.
    6. If the user is not found or if the query is missing, appropriate error responses are returned.
    
    Returns:
        - 200: Successfully processed the query with results.
        - 400: Missing query.
        - 404: User not found.
    """
    current_user_id = get_jwt_identity() # Get the current user's ID from the JWT
    user = execute_query(
        'SELECT name FROM user_details WHERE id = ?', (current_user_id,), fetch_one=True
    )
    if user:
        name = user[0]
        data = request.get_json()
        query = data['query']
        if not query:
            return jsonify({'message': 'Missing query'}), 400
        sql_query = ask(query) # Process the query using the bot
        print(sql_query)
        answer = execute_query(sql_query, fetch_all=True)  # Execute the SQL query 
        print(answer)    
        return jsonify({'current_user': name, 'sql_query':sql_query, 'response': f'The answer for {query} is :\n\n {answer}'}), 200
    return jsonify({'message': 'User not found'}), 404



# Admin-only endpoint
@app.route('/admin', methods=['GET'])
@jwt_required()
@role_required([0])  # Only accessible by admins
def admin_resource():
    """
    Admin Resource Endpoint:
    
    This endpoint is accessible only to users with admin roles. It provides a welcome message and user details.
    The following steps are performed:
    
    1. The current user's ID is retrieved from the JWT token.
    2. The user's details are fetched from the database based on the ID.
    3. A response is returned with a welcome message and the user's details.
    
    Returns:
        - 200: Welcome message with user details.
    """
    current_user_id = get_jwt_identity()
    user = execute_query(
        'SELECT * FROM user_details WHERE id = ?', (current_user_id,), fetch_one=True
    )
    username = user[2]
    role = user[1]
    name = user[4]
    karma = user[5]
    return jsonify({'message': f'Welcome to Admin page!','username':username,'name':name,'role':role,'karma':karma}), 200



# Admin and MOD-only endpoint
@app.route('/mod', methods=['GET'])
@jwt_required()
@role_required([0,1])  # Only accessible by mods
def mod_resource():
    """
    Moderator Resource Endpoint:
    
    This endpoint is accessible only to users with admin or moderator roles. It provides a welcome message and user details.
    The following steps are performed:
    
    1. The current user's ID is retrieved from the JWT token.
    2. The user's details are fetched from the database based on the ID.
    3. A response is returned with a welcome message and the user's details.
    
 Returns:
        - 200: Welcome message with user details.
    """
    current_user_id = get_jwt_identity()
    user = execute_query(
        'SELECT * FROM user_details WHERE id = ?', (current_user_id,), fetch_one=True
    )
    username = user[2]
    role = user[1]
    name = user[4]
    karma = user[5]
    return jsonify({'message': f'Welcome to Moderator page!','username':username,'name':name,'role':role,'karma':karma}), 200



#Accessible by everyone
@app.route('/user', methods=['GET'])
@jwt_required()
@role_required([0,1,2])  # Only accessible by users
def user_resource():
    """
    User Resource Endpoint:
    
    This endpoint is accessible to all authenticated users, regardless of their role. It provides a welcome message and user details.
    The following steps are performed:
    
    1. The current user's ID is retrieved from the JWT token.
    2. The user's details are fetched from the database based on the ID.
    3. A response is returned with a welcome message and the user's details.
    
    Returns:
        - 200: Welcome message with user details.
    """
    current_user_id = get_jwt_identity()
    user = execute_query(
        'SELECT * FROM user_details WHERE id = ?', (current_user_id,), fetch_one=True
    )
    username = user[2]
    role = user[1]
    name = user[4]
    karma = user[5]
    return jsonify({'message': f'Welcome to User page!','username':username,'name':name,'role':role,'karma':karma}), 200


# Initialize database on app startup
with app.app_context():
    create_table()

if __name__ == "__main__":
    app.run(debug=True)
