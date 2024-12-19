import base64
import os

from flask import Blueprint, request, jsonify, session, current_app, send_from_directory
from werkzeug.exceptions import Unauthorized

from config import Config
from services.file_service import FileService

prediction_blueprint = Blueprint('prediction', __name__)

file_service = FileService(upload_folder=Config.UPLOAD_FOLDER, allowed_extensions=Config.ALLOWED_EXTENSIONS)


@prediction_blueprint.route('/predict', methods=['POST'])
def predict():
    with current_app.app_context():
        prediction_service = current_app.prediction_service

        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image part in the request'}), 400

        try:
            image_data = data['image'].split(",")[1] if "," in data['image'] else data['image']
            filepath = file_service.save_base64_file(image_data)
        except Exception as e:
            current_app.logger.error(f"Error decoding or saving base64 image: {e}")
            return jsonify({'error': 'Invalid image data'}), 400

        try:
            predicted_class, confidence, text_detected = prediction_service.predict(filepath)
            user_id = session.get('user_id')
            prediction_id = prediction_service.save_prediction(user_id, filepath, predicted_class, confidence)
            with open(os.path.join(Config.UPLOAD_FOLDER, filepath), "rb") as image_file:
                base64_encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                base64_image_data = f"data:image/jpeg;base64,{base64_encoded_image}" ##tu


            return jsonify({
                'title': predicted_class,
                'confidence': str(confidence),
                'image_src': base64_image_data,
                'filename': filepath,
                'message': 'Prediction saved successfully',
                'prediction_id': prediction_id,
                'text_detected': text_detected
            }), 200
        except Exception as e:
            current_app.logger.error(f"Error during prediction: {e}")
            return jsonify({'error': 'Error during prediction'}), 500


@prediction_blueprint.route('/user-predictions', methods=['GET'])
def user_predictions():
    with current_app.app_context():
        if 'user_id' not in session:
            raise Unauthorized('Unauthorized')

        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit

        try:
            predictions, total_count = current_app.prediction_service.get_user_predictions_paginated(
                session['user_id'], limit, offset
            )

            has_more = offset + limit < total_count

            return jsonify({
                'predictions': predictions,
                'has_more': has_more,
                'total_count': total_count
            }), 200
        except Exception as e:
            current_app.logger.error(f"Error fetching predictions: {e}")
            return jsonify({'error': 'Error fetching predictions'}), 400


@prediction_blueprint.route('/uploads/<filename>', methods=['GET'])
def uploaded_file(filename):
    try:
        decoded_filename = filename.rsplit('/', 1)[-1]
        return send_from_directory(Config.UPLOAD_FOLDER, decoded_filename)
    except Exception as e:
        with current_app.app_context():
            current_app.logger.error(f"Error serving file {filename}: {e}")
        return jsonify({'error': 'File not found'}), 404
