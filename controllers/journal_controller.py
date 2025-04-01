from models.completed_routes_model import CompletedRoute
from models.routes_model import Route
from config.db_config import db
from sqlalchemy.sql import func
from datetime import datetime

def get_journal_entries_by_user(user_id):
    """
    Hämtar alla journalanteckningar (genomförda klätterrutter) för en specifik användare.
    
    Denna funktion sammanfogar CompletedRoute och Route för att returnera detaljerad
    information om varje genomförd rutt, inklusive svårighetsgrad och ruttyp.
    
    Args:
        user_id (int): ID för användaren vars journalanteckningar ska hämtas
        
    Returns:
        tuple: (list, str or None)
            - Vid lyckad hämtning: (lista med journalanteckningar, None)
            - Vid fel: (None, felmeddelande)
            
    Exempel på returdata vid lyckat anrop:
    [
        {
            'id': 1,
            'route_id': 5,
            'user_id': 3,
            'date': '2025-03-15T14:30:00',
            'flash': True,
            'image_url': 'https://imgur.com/example.jpg',
            'route_type': 'boulder',
            'difficulty': '7A'
        },
        ...
    ]
    """
    try:
        completed_routes = (CompletedRoute.query
            .filter_by(user_id=user_id)
            .join(Route, CompletedRoute.route_id == Route.id)
            .add_entity(Route)
            .all())
        
        result = [{
            'id': cr.CompletedRoute.id,
            'route_id': cr.CompletedRoute.route_id,
            'user_id': cr.CompletedRoute.user_id,
            'date': cr.CompletedRoute.date.isoformat() if cr.CompletedRoute.date else None,
            'flash': cr.CompletedRoute.flash,
            'image_url': cr.CompletedRoute.image_url,
            'route_type': cr.Route.type,
            'difficulty': cr.Route.difficulty.grade if cr.Route.difficulty else None
        } for cr in completed_routes]
        
        return result, None
    except Exception as e:
        db.session.rollback()
        return None, f"Database error: {str(e)}"

def get_journal_entry_by_id(entry_id):
    """
    Hämtar en specifik journalanteckning (genomförd klätterrutt) med angivet ID.
    
    Denna funktion sammanfogar CompletedRoute och Route för att returnera detaljerad
    information om den efterfrågade journalanteckningen, inklusive svårighetsgrad och ruttyp.
    
    Args:
        entry_id (int): ID för journalanteckningen som ska hämtas
        
    Returns:
        tuple: (dict, str or None)
            - Vid lyckad hämtning: (journalanteckning som dictionary, None)
            - Vid fel eller om anteckningen inte finns: (None, felmeddelande)
            
    Exempel på returdata vid lyckat anrop:
    {
        'id': 1,
        'route_id': 5,
        'user_id': 3,
        'date': '2025-03-15T14:30:00',
        'flash': True,
        'image_url': 'https://imgur.com/example.jpg',
        'route_type': 'boulder',
        'difficulty': '7A'
    }
    """
    try:
        completed_route = (CompletedRoute.query
            .filter_by(id=entry_id)
            .join(Route, CompletedRoute.route_id == Route.id)
            .add_entity(Route)
            .first())
        
        if not completed_route:
            return None, "Journal entry not found"
        
        result = {
            'id': completed_route.CompletedRoute.id,
            'route_id': completed_route.CompletedRoute.route_id,
            'user_id': completed_route.CompletedRoute.user_id,
            'date': completed_route.CompletedRoute.date.isoformat() if completed_route.CompletedRoute.date else None,
            'flash': completed_route.CompletedRoute.flash,
            'image_url': completed_route.CompletedRoute.image_url,
            'route_type': completed_route.Route.type,
            'difficulty': completed_route.Route.difficulty.grade if completed_route.Route.difficulty else None
        }
        
        return result, None
    except Exception as e:
        db.session.rollback()
        return None, f"Database error: {str(e)}"

def create_journal_entry(user_id, route_id, flash=False, image_url=None, date=None):
    """
    Skapar en ny journalanteckning (genomförd klätterrutt).
    
    Verifierar att den angivna rutten existerar innan en ny journalanteckning skapas.
    Om inget datum anges, används aktuellt datum och tid.
    
    Args:
        user_id (int): ID för användaren som skapade anteckningen
        route_id (int): ID för klätterrutten som genomfördes
        flash (bool, optional): Om rutten klarades på första försöket. Default: False
        image_url (str, optional): URL till en bild av genomförd rutt. Default: None
        date (datetime, optional): Datum och tid för genomförd rutt. Default: Aktuell tid
        
    Returns:
        tuple: (dict, str or None)
            - Vid lyckad skapelse: (journalanteckning som dictionary, None)
            - Vid fel: (None, felmeddelande)
            
    Exempel på returdata vid lyckat anrop:
    {
        'id': 42,
        'user_id': 3,
        'route_id': 7,
        'date': '2025-04-01T15:30:45',
        'flash': True,
        'image_url': 'https://imgur.com/example.jpg'
    }
    """
    try:
        # Check if route exists
        route = Route.query.get(route_id)
        if not route:
            return None, "Route not found"
        
        # Create new completed route
        new_entry = CompletedRoute(
            user_id=user_id,
            route_id=route_id,
            flash=flash,
            image_url=image_url
        )
        
        # Set date if provided, otherwise default is used (current timestamp)
        if date:
            new_entry.date = date
        
        db.session.add(new_entry)
        db.session.commit()
        
        return {
            'id': new_entry.id,
            'user_id': new_entry.user_id,
            'route_id': new_entry.route_id,
            'date': new_entry.date.isoformat(),
            'flash': new_entry.flash,
            'image_url': new_entry.image_url
        }, None
    except Exception as e:
        db.session.rollback()
        return None, f"Database error: {str(e)}"

def update_journal_entry(entry_id, route_id=None, flash=None, image_url=None, date=None):
    """
    Uppdaterar en befintlig journalanteckning (genomförd klätterrutt).
    
    Uppdaterar endast de fält som skickats med, övriga fält förblir oförändrade.
    Om ett nytt route_id anges, verifieras att rutten existerar.
    
    Args:
        entry_id (int): ID för journalanteckningen som ska uppdateras
        route_id (int, optional): Nytt ID för klätterrutten. Default: None (ingen ändring)
        flash (bool, optional): Uppdaterad flash-status. Default: None (ingen ändring)
        image_url (str, optional): Ny URL till en bild. Default: None (ingen ändring)
        date (datetime, optional): Nytt datum och tid. Default: None (ingen ändring)
        
    Returns:
        tuple: (dict, str or None)
            - Vid lyckad uppdatering: (uppdaterad journalanteckning som dictionary, None)
            - Vid fel: (None, felmeddelande)
            
    Exempel på returdata vid lyckat anrop:
    {
        'id': 42,
        'user_id': 3,
        'route_id': 7,
        'date': '2025-04-01T15:30:45',
        'flash': True,
        'image_url': 'https://imgur.com/example.jpg'
    }
    """
    try:
        entry = CompletedRoute.query.get(entry_id)
        if not entry:
            return None, "Journal entry not found"
        
        # Update only the provided fields
        if route_id is not None:
            # Verify route exists
            route = Route.query.get(route_id)
            if not route:
                return None, "Route not found"
            entry.route_id = route_id
        
        if flash is not None:
            entry.flash = flash
            
        if image_url is not None:
            entry.image_url = image_url
            
        if date is not None:
            entry.date = date
        
        db.session.commit()
        
        return {
            'id': entry.id,
            'user_id': entry.user_id,
            'route_id': entry.route_id,
            'date': entry.date.isoformat(),
            'flash': entry.flash,
            'image_url': entry.image_url
        }, None
    except Exception as e:
        db.session.rollback()
        return None, f"Database error: {str(e)}"

def delete_journal_entry(entry_id):
    """
    Tar bort en journalanteckning (genomförd klätterrutt) från databasen.
    
    Args:
        entry_id (int): ID för journalanteckningen som ska tas bort
        
    Returns:
        tuple: (dict, str or None)
            - Vid lyckad borttagning: (bekräftelsemeddelande som dictionary, None)
            - Vid fel: (None, felmeddelande)
            
    Exempel på returdata vid lyckat anrop:
    {
        'message': 'Journal entry 42 deleted successfully'
    }
    """
    try:
        entry = CompletedRoute.query.get(entry_id)
        if not entry:
            return None, "Journal entry not found"
        
        db.session.delete(entry)
        db.session.commit()
        
        return {'message': f'Journal entry {entry_id} deleted successfully'}, None
    except Exception as e:
        db.session.rollback()
        return None, f"Database error: {str(e)}"