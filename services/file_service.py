import os
import time
import uuid

class FileService:
    def __init__(self, upload_folder, allowed_extensions):
        self.upload_folder = upload_folder
        self.allowed_extensions = allowed_extensions


        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)

    def allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    def save_file(self, file):
        unique_id = uuid.uuid4()
        # Get the current timestamp
        timestamp = int(time.time())
        # Get the file extension
        _, extension = os.path.splitext(file.filename)
        # Create a unique filename using UUID and timestamp
        unique_filename = f"{unique_id}_{timestamp}{extension}"
        # Define the full path where the file will be saved
        filepath = os.path.join(self.upload_folder, unique_filename)
        print(f"Saving file to: {filepath}")

        try:
            file.save(filepath)
            print(f"File saved successfully: {filepath}")
        except Exception as e:
            print(f"Error saving file: {e}")
            raise e

        return unique_filename
