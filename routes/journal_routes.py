from flask import Blueprint, jsonify, request
from controllers.journal_controller import (
    get_journal_entries_by_user, 
    get_journal_entry_by_id, 
    create_journal_entry, 
    update_journal_entry, 
    delete_journal_entry
)
from controllers.route_controller import create_route
from datetime import datetime
from utils.auth_decorator import auth_required

journal_routes = Blueprint('journal_routes', __name__)


@journal_routes.route('/', methods=['GET'])
@auth_required
def get_user_journal(current_user):
    entries, error = get_journal_entries_by_user(current_user.id)
    if error:
        return jsonify({'error': error}), 404
    
    return jsonify({'entries': entries}), 200

@journal_routes.route('/post', methods=['POST'])
@auth_required
def post_journal_entry(current_user):
    """Create a new journal entry with auto-route creation"""
    data = request.get_json()
    
    # Debug the received data
    print(f"Received data for journal entry: {data}")
    
    # Validate required fields for route creation
    if 'route_type' not in data or 'difficulty' not in data:
        return jsonify({'error': 'Missing required fields: route_type and difficulty'}), 400
    
    try:
        # Create route first
        route_data = {
            'type': data['route_type'],
            'difficulty': data['difficulty'],
            'location': data.get('location'),
            'description': data.get('description')
        }
        
        new_route, route_error = create_route(route_data)
        if route_error:
            return jsonify({'error': f'Route creation failed: {route_error}'}), 400
        
        # Then create journal entry
        flash = bool(data.get('flash', False))
        image_url = data.get('image_url')
        
        # Parse date if provided
        date = None
        if 'date' in data and data['date']:
            try:
                date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use ISO format (YYYY-MM-DDThh:mm:ss)'}), 400
        
        # Create journal entry with new route ID
        entry_data, error = create_journal_entry(
            user_id=current_user.id,
            route_id=new_route['id'],
            flash=flash,
            image_url=image_url,
            date=date
        )
        
        if error:
            return jsonify({'error': error}), 400
        
        # Combine route and entry data for response
        response_data = entry_data.copy()
        response_data.update({
            'route_type': new_route['type'],
            'difficulty': new_route['difficulty'],
            'location': new_route.get('location'),
            'description': new_route.get('description')
        })
        
        return jsonify(response_data), 201
        
    except Exception as e:
        print(f"Error in post_journal_entry: {str(e)}")
        return jsonify({'error': str(e)}), 500

@journal_routes.route('/edit/<int:entry_id>', methods=['GET', 'PUT', 'DELETE'])
@auth_required
def edit_journal_entry(entry_id, current_user):
    """Get, update, or delete a specific journal entry"""
    if request.method == 'GET':
        """Get a specific journal entry"""
        entry_data, error = get_journal_entry_by_id(entry_id)
        if error:
            return jsonify({'error': error}), 404
        
        # Verify user owns this entry
        if entry_data['user_id'] != current_user.id:
            return jsonify({'error': 'Unauthorized access to this journal entry'}), 403
            
        return jsonify({'entry': entry_data}), 200

    elif request.method == 'PUT':
        """Update a specific journal entry"""
        # Get current entry to verify ownership
        current_entry, error = get_journal_entry_by_id(entry_id)
        if error:
            return jsonify({'error': error}), 404
            
        # Check if user owns this entry
        if current_entry['user_id'] != current_user.id:
            return jsonify({'error': 'Unauthorized to edit this journal entry'}), 403
        
        data = request.get_json()
        print(f"Editing journal entry {entry_id} with data: {data}")
        
        # Parse fields
        flash = bool(data.get('flash', False))
        image_url = data.get('image_url')
        difficulty = data.get('difficulty')  # Get the new difficulty
        route_type = data.get('route_type')  # Get the new route type
        
        # Parse date if provided
        date = None
        if 'date' in data and data['date']:
            try:
                date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use ISO format (YYYY-MM-DDThh:mm:ss)'}), 400
        
        # Update entry
        updated_entry, error = update_journal_entry(
            entry_id=entry_id,
            flash=flash,
            image_url=image_url,
            date=date,
            difficulty=difficulty,  # Pass the difficulty to update the route
            route_type=route_type   # Pass the route type to update the route
        )
        
        if error:
            return jsonify({'error': error}), 400
            
        return jsonify({'message': 'Journal entry updated successfully', 'entry': updated_entry}), 200

    elif request.method == 'DELETE':
        """Delete a specific journal entry"""
        # Get current entry to verify ownership
        current_entry, error = get_journal_entry_by_id(entry_id)
        if error:
            return jsonify({'error': error}), 404
            
        # Check if user owns this entry
        if current_entry['user_id'] != current_user.id:
            return jsonify({'error': 'Unauthorized to delete this journal entry'}), 403
            
        result, error = delete_journal_entry(entry_id)
        if error:
            return jsonify({'error': error}), 400
            
        return jsonify(result), 200