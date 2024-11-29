from flask import jsonify
from functools import wraps
from flask_jwt_extended import get_jwt_identity
from models import execute_query



#This decorator checks if the role required matches with the current role
def role_required(required_role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            # Query the database to get the user's role based on their ID
            user = execute_query(
                'SELECT role FROM user_details WHERE id = ?', (current_user_id,), fetch_one=True
            )
            if not user:
                return jsonify({'message': 'User not found'}), 404
            # Check if the user's role is in the list of required roles
            if user[0] not in required_role:
                 # If not, reduce the user's karma by 1
                result = execute_query('UPDATE user_details SET karma = karma - 1 WHERE id = ?', (current_user_id,),fetch_one=True,commit=True)

                print("karma reduced", result)
                return jsonify({'message': 'You do not have permission to access this resource. Your karma was reduced'}), 403
            # If the user has the required role, increase their karma by 0.1
            result = execute_query('UPDATE user_details SET karma = karma + 0.1 WHERE id = ?', (current_user_id,),fetch_one=True,commit=True)
            # Proceed to execute the decorated function
            return func(*args, **kwargs)
        return wrapper
    return decorator