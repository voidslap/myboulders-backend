import os
import sys

# TODO: Fixa så bild URLen returnar enbart image URL och inte en download länk
# När allt funkar se till att ta bort all skit som användes för testing


# Add the project root to Python path for proper imports
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config.db_config import db
from models.completed_routes_model import CompletedRoute
from models.users_model import User

SCOPES = ['https://www.googleapis.com/auth/drive.file']  # Endast dina egna uppladdade filer


def authenticate_google_drive():
    creds = None
    # Har vi redan token?
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Om inte: kör OAuth-flödet i webbläsaren
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)

        # Spara access token för framtida användning
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())

    return creds


def upload_image(service, filepath):
    file_metadata = {'name': os.path.basename(filepath)}
    media = MediaFileUpload(filepath, mimetype='image/jpeg')  # ändra vid behov

    # Ladda upp filen
    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    file_id = uploaded_file.get('id')
    
    # Gör filen publik
    service.permissions().create(
        fileId=file_id,
        body={'role': 'reader', 'type': 'anyone'}
    ).execute()

    # Hämta delbar URL
    file = service.files().get(fileId=file_id, fields='webViewLink, webContentLink').execute()

    return file.get('webViewLink'), file.get('webContentLink')  # webContentLink = direktnedladdning


#
# !!!! Denna ska kanske läggas i en annan controller? T.ex db_controller.py?? !!!!
#
def post_img_to_db(view_link, direct_link, target_type, target_id, **kwargs):
    """
    Spara bildlänkar till databasen.
    
    Args:
        view_link (str): Länk till webbvisning av bilden
        direct_link (str): Direktlänk för nedladdning av bilden
        target_type (str): Antingen 'completed_route' eller 'user_profile'
        target_id (int): ID för användaren eller den genomförda rutten
        **kwargs: Extra parametrar baserat på target_type
            Om target_type='completed_route', behövs:
                - user_id (int): Användar-ID
                - route_id (int): Rutt-ID
                - flash (bool, optional): Om rutten klarades som flash
            Om target_type='user_profile', behövs inga extra parametrar
                
    Returns:
        tuple: (objekt, felmeddelande eller None)
    """
    try:
        if target_type == 'completed_route':
            user_id = kwargs.get('user_id')
            route_id = kwargs.get('route_id')
            flash = kwargs.get('flash', False)
            
            # Kontrollera om den genomförda rutten redan finns
            existing = CompletedRoute.query.get(target_id) if target_id else None
            
            if existing:
                # Uppdatera befintlig genomförd rutt
                existing.image_url = direct_link
                db.session.commit()
                return existing, None
            else:
                # Skapa ny genomförd rutt med bild
                new_completed_route = CompletedRoute(
                    id=target_id if target_id else None,
                    user_id=user_id,
                    route_id=route_id,
                    flash=flash,
                    image_url=direct_link
                )
                db.session.add(new_completed_route)
                db.session.commit()
                return new_completed_route, None
                
        elif target_type == 'user_profile':
            # Uppdatera användarens profilbild
            user = User.query.get(target_id)
            if not user:
                return None, "Användaren hittades inte"
                
            user.profile_image_url = direct_link
            db.session.commit()
            return user, None
            
        else:
            return None, "Ogiltig target_type. Använd 'completed_route' eller 'user_profile'."
            
    except Exception as e:
        db.session.rollback()
        return None, f"Databasfel: {str(e)}"


def create_drive_service():
    """Helper function to create and return an authenticated Drive service"""
    creds = authenticate_google_drive()
    return build('drive', 'v3', credentials=creds)


if __name__ == '__main__':
    # Handle as a script when run directly
    
    # 1. Import Flask app to get application context
    try:
        from app import app
        
        # Check for command line arguments
        if len(sys.argv) > 1:
            filepath = sys.argv[1]  # Use command line argument as filepath
        else:
            filepath = input("Enter path to image file: ")  # Ask for filepath
        
        print(f"Uploading image: {filepath}")
        
        # Create service and upload image
        service = create_drive_service()
        view_link, direct_link = upload_image(service, filepath)
        
        print("🔗 Web View Link:", view_link)
        print("⬇️ Direct Download Link:", direct_link)
        
        # Ask if user wants to save to database
        save_to_db = input("Do you want to save this image to the database? (y/n): ")
        
        if save_to_db.lower() == 'y':
            target_type = input("Enter target type (completed_route/user_profile): ")
            
            with app.app_context():
                if target_type == 'completed_route':
                    user_id = int(input("Enter user ID: "))
                    route_id = int(input("Enter route ID: "))
                    flash_input = input("Flash? (y/n): ")
                    flash = flash_input.lower() == 'y'
                    
                    result, error = post_img_to_db(
                        view_link, 
                        direct_link,
                        target_type='completed_route',
                        target_id=None,
                        user_id=user_id,
                        route_id=route_id,
                        flash=flash
                    )
                
                elif target_type == 'user_profile':
                    user_id = int(input("Enter user ID: "))
                    
                    result, error = post_img_to_db(
                        view_link,
                        direct_link,
                        target_type='user_profile',
                        target_id=user_id
                    )
                
                else:
                    print("Invalid target type.")
                    sys.exit(1)
                
                if error:
                    print(f"Error: {error}")
                else:
                    print(f"Image saved successfully: {result}")
                
    except ImportError as e:
        print(f"Error importing Flask app: {e}")
        print("\nThis script must be run from the project root or in the Flask application context.")
        print("Try running it with: python -m controllers.google_controller")
    except Exception as e:
        print(f"Error: {e}")