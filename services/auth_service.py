from flask import session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text

class AuthService:
    def __init__(self, db):
        self.db = db

    def register_user(self, username, password):
        db_session = self.db.session

        try:
            query = text('SELECT * FROM users WHERE username = :username')
            existing_user = db_session.execute(query, {'username': username}).fetchone()

            if existing_user:
                raise ValueError("User with this username already exists")

            hashed_password = generate_password_hash(password)
            query = text('INSERT INTO users (username, password) VALUES (:username, :password) RETURNING id')
            result = db_session.execute(query, {
                'username': username,
                'password': hashed_password
            })

            user_id = result.fetchone()[0]
            db_session.commit()
            return {'user_id': user_id}
        except ValueError as ve:
            db_session.rollback()
            with current_app.app_context():
                current_app.logger.warning(f"User registration error: {ve}")
            raise ve
        except Exception as e:
            db_session.rollback()
            with current_app.app_context():
                current_app.logger.error(f"Unexpected error during user registration: {e}")
            raise e
        finally:
            db_session.close()

    def login_user(self, username, password):
        db_session = self.db.session
        try:
            query = text('SELECT * FROM users WHERE username = :username')
            user = db_session.execute(query, {'username': username}).fetchone()

            if not user:
                return None, 'User not found'

            if not check_password_hash(user[2], password):
                return None, 'Invalid password'

            return {'user_id': user[0]}, None
        except Exception as e:
            with current_app.app_context():
                current_app.logger.error(f"Error logging in user {username}: {e}")
            raise e
        finally:
            db_session.close()

    def logout_user(self):
        try:
            session.clear()
            self.db.session.commit()
            return {'message': 'User successfully logged out'}
        except Exception as e:
            self.db.session.rollback()
            with current_app.app_context():
                current_app.logger.error(f"Error logging out user: {e}")
            raise e
        finally:
            self.db.session.close()

    def get_user_by_id(self, user_id):
        db_session = self.db.session
        try:
            query = text('SELECT id, username FROM users WHERE id = :user_id')
            result = db_session.execute(query, {'user_id': user_id})
            user = result.fetchone()

            if user:
                return {'id': user[0], 'username': user[1]}
            else:
                return None
        except Exception as e:
            with current_app.app_context():
                current_app.logger.error(f"Error fetching user with ID {user_id}: {e}")
            raise e
        finally:
            db_session.close()

    def close(self):
        self.db.session.close()
