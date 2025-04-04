from flask import Blueprint, jsonify, request
from controllers.image_controller import save_image, upload_to_imgur, post_img_to_db
import requests
import os
from werkzeug.utils import secure_filename
import base64
from utils.auth_decorator import auth_required

image_routes = Blueprint('image_routes', __name__)

IMGUR_CLIENT_ID = os.getenv('IMGUR_CLIENT_ID')
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@image_routes.route('/upload', methods=['POST'])
@auth_required
def upload_image(current_user):
    """
    Ladda upp en bild till servern, Imgur och eventuellt databasen.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Check file type
    if not allowed_file(file.filename):
        return jsonify({'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400

    # Check file size
    file_data = file.read()
    if len(file_data) > MAX_FILE_SIZE:
        return jsonify({'error': f'File too large. Maximum size: {MAX_FILE_SIZE/1024/1024}MB'}), 400

    # Reset file pointer
    file.seek(0)

    # Steg 1: Spara bilden lokalt med randomiserat filnamn
    filepath = save_image(file)

    if not filepath:
        return jsonify({'error': 'Failed to save image'}), 500

    try:
        # Steg 2: Ladda upp till Imgur
        headers = {'Authorization': f'Client-ID {IMGUR_CLIENT_ID}'}
        response = requests.post(
            'https://api.imgur.com/3/image',
            headers=headers,
            data={
                'image': base64.b64encode(file_data),
                'type': 'base64'
            }
        )

        response_data = response.json()

        if not response_data['success']:
            return jsonify({'error': 'Failed to upload image to Imgur'}), 500

        image_url = response_data['data']['link']

        # Steg 3: Ta bort den lokala filen
        if os.path.exists(filepath):
            os.remove(filepath)

        # Steg 4: Om target_type och target_id finns, spara till databasen
        target_type = request.form.get('target_type')
        target_id = request.form.get('target_id')

        if target_type and target_id:
            # Samla in extra parametrar för databasen
            kwargs = {}
            if target_type == 'completed_route':
                kwargs['user_id'] = current_user.id  # Använd current_user
                kwargs['route_id'] = request.form.get('route_id')
                kwargs['flash'] = request.form.get('flash') == 'true'

            # Spara till databasen
            result, db_error = post_img_to_db(
                image_url,
                target_type,
                int(target_id),
                **kwargs
            )

            if db_error:
                # Vi returnerar URL:en även om databaslagringen misslyckades
                return jsonify({
                    'image_url': image_url,
                    'warning': f'Image uploaded but database save failed: {db_error}'
                }), 200

        # Steg 5: Returnera URL:en
        return jsonify({'image_url': image_url}), 200

    except Exception as e:
        # Försök ta bort filen om något går fel
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)

        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

@image_routes.route('/upload/registration', methods=['POST'])
def upload_registration_image():
    """
    Special endpoint for uploading profile images during user registration.
    No authentication required.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Check file type
    if not allowed_file(file.filename):
        return jsonify({'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
    
    # Check file size
    file_data = file.read()
    if len(file_data) > MAX_FILE_SIZE:
        return jsonify({'error': f'File too large. Maximum size: {MAX_FILE_SIZE/1024/1024}MB'}), 400
    
    # Reset file pointer
    file.seek(0)

    try:
        # Save image and upload to Imgur
        filepath = save_image(file)
        
        if not filepath:
            return jsonify({'error': 'Failed to save image'}), 500
        
        # Upload to Imgur
        image_url, error = upload_to_imgur(filepath)
        
        if error:
            return jsonify({'error': f'Failed to upload image: {error}'}), 500
        
        # Remove local file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # Return only the image URL
        return jsonify({'image_url': image_url}), 200
        
    except Exception as e:
        # Clean up if error
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

@image_routes.route('/delete', methods=['DELETE'])
@auth_required
def delete_image(current_user):
    data = request.get_json()
    if 'delete_hash' not in data:
        return jsonify({'error': 'Missing delete_hash parameter'}), 400
    
    try:
        headers = {'Authorization': f'Client-ID {IMGUR_CLIENT_ID}'}
        response = requests.delete(
            f'https://api.imgur.com/3/image/{data["delete_hash"]}',
            headers=headers
        )
        
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'message': 'Image deleted successfully'
            }), 200
        else:
            return jsonify({'error': 'Failed to delete image from Imgur'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Image deletion error: {str(e)}'}), 500
