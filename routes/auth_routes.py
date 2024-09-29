from flask import Blueprint, request, session, jsonify, current_app

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/check-session', methods=['GET'])
def check_session():
    logged_in = 'user_id' in session
    return jsonify({'loggedIn': logged_in}), 200

@auth_blueprint.route('/get-username', methods=['GET'])
def get_username():
    if 'user_id' in session:
        user_id = session['user_id']
        user = current_app.auth_service.get_user_by_id(user_id)
        return jsonify({'username': user['email']}), 200
    return jsonify({'error': 'User not logged in'}), 401

@auth_blueprint.route('/register', methods=['POST'])
def register():
    auth_service = current_app.auth_service

    try:
        email = request.json.get('email')
        password = request.json.get('password')

        # Register the user and handle different possible errors
        result = auth_service.register_user(email, password)
        session['user_id'] = result['user_id']
        return jsonify({'message': 'User registered', 'user_id': result['user_id']}), 201
    except ValueError as ve:
        # Handle specific validation errors
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        print(f"Error registering user: {e}")
        return jsonify({'error': 'An unexpected error occurred during registration'}), 500

@auth_blueprint.route('/login', methods=['POST'])
def login():
    auth_service = current_app.auth_service

    try:
        email = request.json.get('email')
        password = request.json.get('password')

        user, error = auth_service.login_user(email, password)

        if error:
            return jsonify({'error': error}), 400

        session['user_id'] = user['user_id']
        return jsonify({'message': 'User logged in'}), 200
    except Exception as e:
        print(f"Error logging in: {e}")
        return jsonify({'error': 'An unexpected error occurred during login'}), 500

@auth_blueprint.route('/logout', methods=['GET'])
def logout():
    try:
        session.pop('user_id', None)
        return jsonify({'message': 'User logged out'}), 200
    except Exception as e:
        print(f"Error logging out: {e}")
        return jsonify({'error': 'Error logging out'}), 500
