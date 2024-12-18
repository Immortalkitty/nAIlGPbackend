import os
import torch
from PIL import Image
from sqlalchemy import text
from torchvision import transforms
from config import Config
from models.model_initializer import ModelInitializer
from flask import current_app


class PredictionService:
    def __init__(self, model_path, db, device='cpu'):
        self.model_path = model_path
        self.device = torch.device(device)
        self.model = self.load_model()
        self.db = db

    def load_model(self):
        try:
            print(f"Loading PyTorch model from {self.model_path}...")
            model_initializer = ModelInitializer(self.device, model_name='Inception_V3', weights_suffix='DEFAULT')
            model = model_initializer.initialize_model()
            model.load_state_dict(torch.load(self.model_path, map_location=self.device))
            model.eval()
            print("Model loaded successfully.")
            return model
        except Exception as e:
            print(f"Error loading PyTorch model: {e}")
            raise e

    def preprocess_image(self, image_path):
        if not os.path.exists(image_path):
            with current_app.app_context():
                current_app.logger.error(f"Image path {image_path} does not exist.")
            return None

        with current_app.app_context():
            current_app.logger.info(f"Loading and preprocessing image from {image_path}...")

        preprocess = transforms.Compose([
            transforms.Resize(310),
            transforms.CenterCrop(299),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        img = Image.open(image_path).convert('RGB')
        img_tensor = preprocess(img).unsqueeze(0)
        return img_tensor.to(self.device)

    def predict(self, image_path):
        image_path = os.path.join(Config.UPLOAD_FOLDER, image_path)
        img_tensor = self.preprocess_image(image_path)

        if img_tensor is None:
            return "Error", 0.0

        img_tensor = img_tensor.to(self.device)

        with torch.no_grad():
            outputs = self.model(img_tensor)
            if isinstance(outputs, tuple):
                outputs = outputs[0]
            prediction_value = torch.sigmoid(outputs).item()

        predicted_class = "Healthy" if prediction_value < 0.5 else "Infected"
        confidence = 1 - prediction_value if prediction_value < 0.5 else prediction_value

        return predicted_class, confidence

    def save_prediction(self, user_id, filepath, title, confidence):
        db_session = self.db.session
        try:
            query = text(
                'INSERT INTO predictions (user_id, image_src, title, confidence) VALUES (:user_id, :image_src, :title, :confidence) RETURNING id'
            )
            result = db_session.execute(query, {
                'user_id': user_id,
                'image_src': filepath,
                'title': title,
                'confidence': confidence
            })
            db_session.commit()
            return result.fetchone()[0]
        except Exception as e:
            db_session.rollback()
            with current_app.app_context():
                current_app.logger.error(f"Error saving prediction: {e}")
            raise e
        finally:
            db_session.close()

    def get_user_predictions_paginated(self, user_id, limit, offset):
        db_session = self.db.session
        try:
            total_query = text('SELECT COUNT(*) FROM predictions WHERE user_id = :user_id')
            total_count = db_session.execute(total_query, {'user_id': user_id}).scalar()

            query = text(
                'SELECT * FROM predictions WHERE user_id = :user_id ORDER BY id DESC LIMIT :limit OFFSET :offset'
            )
            result = db_session.execute(query, {'user_id': user_id, 'limit': limit, 'offset': offset})

            predictions = []
            for row in result.fetchall():
                predictions.append({
                    'id': row[0],
                    'user_id': row[1],
                    'image_src': row[2],
                    'title': row[3],
                    'confidence': str(row[4]),
                    'created_at': row[5].isoformat() if row[5] else None
                })

            return predictions, total_count
        finally:
            db_session.close()
