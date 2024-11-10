from flask import Blueprint, request, session, jsonify, current_app

from services.decrypt_utils import decrypt_message

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
        data = request.get_json()

        encrypted_email = data.get('email')
        encrypted_password = data.get('password')

        if not encrypted_email or not encrypted_password:
            return jsonify({'error': 'Email and password are required'}), 400

        email = decrypt_message(encrypted_email)
        password = decrypt_message(encrypted_password)

        result = auth_service.register_user(email, password)
        session['user_id'] = result['user_id']
        return jsonify({'message': 'User registered', 'user_id': result['user_id']}), 201
    except ValueError as ve:
        with current_app.app_context():
            current_app.logger.warning(f"Validation error during registration: {ve}")
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        with current_app.app_context():
            current_app.logger.error(f"Error registering user: {e}")
        return jsonify({'error': 'An unexpected error occurred during registration'}), 500


@auth_blueprint.route('/login', methods=['POST'])
def login():
    auth_service = current_app.auth_service
    try:
        data = request.get_json()

        encrypted_email = data.get('email')
        encrypted_password = data.get('password')

        if not encrypted_email or not encrypted_password:
            return jsonify({'error': 'Email and password are required'}), 400

        email = decrypt_message(encrypted_email)
        password = decrypt_message(encrypted_password)

        user, error = auth_service.login_user(email, password)

        if error:
            with current_app.app_context():
                current_app.logger.warning(f"Login failed for {email}: {error}")
            return jsonify({'error': error}), 400

        session['user_id'] = user['user_id']
        return jsonify({'message': 'User logged in'}), 200
    except Exception as e:
        with current_app.app_context():
            current_app.logger.error(f"Error logging in: {e}")
        return jsonify({'error': 'An unexpected error occurred during login'}), 500


@auth_blueprint.route('/logout', methods=['GET'])
def logout():
    auth_service = current_app.auth_service
    try:
        response = auth_service.logout_user()
        return jsonify(response), 200
    except Exception as e:
        with current_app.app_context():
            current_app.logger.error(f"Error logging out: {e}")
        return jsonify({'error': 'Error logging out'}), 500
