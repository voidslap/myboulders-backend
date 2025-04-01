from flask import Blueprint, jsonify, request
from controllers.image_controller import save_image, upload_to_imgur, post_img_to_db
import os

image_routes = Blueprint('image_routes', __name__)

@image_routes.route('/upload', methods=['POST'])
def upload_image():
    """
    Ladda upp en bild till servern, Imgur och eventuellt databasen.
    
    Processen:
    1. Sparar bilden lokalt med randomiserat namn
    2. Laddar upp bilden till Imgur
    3. Tar bort den lokala filen
    4. Om target_type och target_id finns, spara länken i databasen
    5. Returnera Imgur URL
    
    Request parameters:
        file: Bilden som ska laddas upp
        target_type (optional): 'completed_route' eller 'user_profile'
        target_id (optional): ID för användare eller genomförd rutt
        
    Returns:
        200 OK med image_url
        400 Bad Request om ingen fil skickades
        500 Internal Server Error om uppladdningen misslyckades
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Steg 1: Spara bilden lokalt med randomiserat filnamn
    filepath = save_image(file)
    
    if not filepath:
        return jsonify({'error': 'Failed to save image'}), 500
    
    try:
        # Steg 2: Ladda upp till Imgur
        image_url, error = upload_to_imgur(filepath)
        
        # Steg 3: Ta bort den lokala filen
        if os.path.exists(filepath):
            os.remove(filepath)
        
        if error:
            return jsonify({'error': f'Failed to upload to Imgur: {error}'}), 500
        
        # Steg 4: Om target_type och target_id finns, spara till databasen
        target_type = request.form.get('target_type')
        target_id = request.form.get('target_id')
        
        if target_type and target_id:
            # Samla in extra parametrar för databasen
            kwargs = {}
            if target_type == 'completed_route':
                kwargs['user_id'] = request.form.get('user_id')
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
