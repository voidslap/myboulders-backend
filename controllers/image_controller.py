import os
import sys
import requests
import base64
import time
from dotenv import load_dotenv

# Add the project root to Python path for proper imports
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from config.db_config import db
from models.completed_routes_model import CompletedRoute
from models.users_model import User

# Ladda miljövariabler
load_dotenv()

# Imgur API-uppgifter
IMGUR_CLIENT_ID = os.getenv('IMGUR_CLIENT_ID')
IMGUR_CLIENT_SECRET = os.getenv('IMGUR_CLIENT_SECRET')
IMGUR_API_URL = 'https://api.imgur.com/3/image'
IMGUR_AUTH_URL = 'https://api.imgur.com/oauth2/token'

# Kontouppgifter för högre uppladdningsgränser
IMGUR_USERNAME = os.getenv('IMGUR_USERNAME')
IMGUR_PASSWORD = os.getenv('IMGUR_PASSWORD')

# Cache för access token
IMGUR_ACCESS_TOKEN = None
IMGUR_TOKEN_EXPIRY = 0


def get_account_token():
    """
    Hämta en access token genom att använda användarnamn och lösenord.
    Detta ger högre uppladdningsgränser (200MB istället för 10MB).
    """
    global IMGUR_ACCESS_TOKEN, IMGUR_TOKEN_EXPIRY
    
    # Om vi redan har en giltig token, använd den
    current_time = time.time()
    if IMGUR_ACCESS_TOKEN and current_time < IMGUR_TOKEN_EXPIRY:
        return IMGUR_ACCESS_TOKEN
    
    # Kontrollera att vi har nödvändiga uppgifter
    if not all([IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET, IMGUR_USERNAME, IMGUR_PASSWORD]):
        print("Saknar Imgur-kontouppgifter. Kommer att använda anonym uppladdning med 10MB gräns.")
        return None
    
    try:
        # Använd Password Grant flow för att autentisera
        response = requests.post(
            IMGUR_AUTH_URL,
            data={
                'client_id': IMGUR_CLIENT_ID,
                'client_secret': IMGUR_CLIENT_SECRET,
                'grant_type': 'password',
                'username': IMGUR_USERNAME,
                'password': IMGUR_PASSWORD
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            IMGUR_ACCESS_TOKEN = data.get('access_token')
            # Token är giltig i 1 månad, men vi sätter den till 28 dagar för säkerhets skull
            IMGUR_TOKEN_EXPIRY = current_time + (28 * 24 * 60 * 60) 
            return IMGUR_ACCESS_TOKEN
        else:
            print(f"Autentisering misslyckades: {response.text}")
            return None
    except Exception as e:
        print(f"Ett fel inträffade vid autentisering: {str(e)}")
        return None


def upload_to_imgur(filepath):
    """
    Ladda upp en bild till Imgur och få direktlänk till bilden.
    Försöker automatiskt använda kontoinloggning för högre uppladdningsgränser om möjligt.
    
    Args:
        filepath (str): Sökväg till bildfilen som ska laddas upp
        
    Returns:
        tuple: (direktlänk till bilden, felmeddelande eller None)
    """
    try:
        # Kontrollera om filen finns
        if not os.path.exists(filepath):
            return None, f"Filen hittades inte: {filepath}"
        
        # Kontrollera filstorlek för att avgöra om vi behöver kontoinloggning
        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        need_account = file_size_mb > 9.5  # Gräns lite under 10MB för säkerhets skull
        
        # Läs bildfilen som binärdata
        with open(filepath, 'rb') as file:
            binary_data = file.read()
        
        # Konvertera bilden till base64
        b64_image = base64.b64encode(binary_data)
        
        # Försök att hämta access token om filen är stor eller om vi explicit vill använda kontoinloggning
        if need_account:
            print(f"Filstorlek: {file_size_mb:.2f}MB - Försöker med kontoinloggning för högre uppladdningsgräns...")
            access_token = get_account_token()
            
            if access_token:
                headers = {
                    'Authorization': f'Bearer {access_token}'
                }
                print("Använder kontoinloggning (200MB gräns).")
            else:
                headers = {
                    'Authorization': f'Client-ID {IMGUR_CLIENT_ID}'
                }
                print(f"Varning: Filen är {file_size_mb:.2f}MB, vilket närmar sig den anonyma gränsen på 10MB.")
                if file_size_mb > 10:
                    return None, f"Filen är för stor ({file_size_mb:.2f}MB). Anonym uppladdning är begränsad till 10MB."
        else:
            # Anonym uppladdning med Client ID
            headers = {
                'Authorization': f'Client-ID {IMGUR_CLIENT_ID}'
            }
            print(f"Använder anonym uppladdning (10MB gräns). Filstorlek: {file_size_mb:.2f}MB")
        
        # Förbereder data för uppladdning
        data = {
            'image': b64_image,
            'type': 'base64',
            'name': os.path.basename(filepath),
            'title': f'MyBoulders upload: {os.path.basename(filepath)}'
        }
        
        # Skicka förfrågan till Imgur API
        response = requests.post(
            IMGUR_API_URL,
            headers=headers,
            data=data
        )
        
        # Kontrollera om uppladdningen lyckades
        if response.status_code == 200:
            json_data = response.json()
            
            if json_data['success']:
                # Hämta direktlänk till bilden
                image_url = json_data['data']['link']
                delete_hash = json_data['data']['deletehash']
                
                print(f"\nUppladdning lyckades!")
                print(f"Bild URL: {image_url}")
                print(f"Delete Hash: {delete_hash} (spara denna om du behöver ta bort bilden senare)\n")
                
                return image_url, None
            else:
                return None, f"Uppladdning misslyckades: {json_data['data']['error']}"
        else:
            return None, f"API-fel: {response.status_code} - {response.text}"
            
    except Exception as e:
        return None, f"Ett fel inträffade: {str(e)}"


def post_img_to_db(image_url, target_type, target_id, **kwargs):
    """
    Spara bildlänkar till databasen.
    
    Args:
        image_url (str): Direktlänk till bilden på Imgur
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
                existing.image_url = image_url
                db.session.commit()
                return existing, None
            else:
                # Skapa ny genomförd rutt med bild
                new_completed_route = CompletedRoute(
                    id=target_id if target_id else None,
                    user_id=user_id,
                    route_id=route_id,
                    flash=flash,
                    image_url=image_url
                )
                db.session.add(new_completed_route)
                db.session.commit()
                return new_completed_route, None
                
        elif target_type == 'user_profile':
            # Uppdatera användarens profilbild
            user = User.query.get(target_id)
            if not user:
                return None, "Användaren hittades inte"
                
            user.profile_image_url = image_url
            db.session.commit()
            return user, None
            
        else:
            return None, "Ogiltig target_type. Använd 'completed_route' eller 'user_profile'."
            
    except Exception as e:
        db.session.rollback()
        return None, f"Databasfel: {str(e)}"


if __name__ == '__main__':
    # Kör som ett fristående skript
    try:
        from app import app
        
        # Kontrollera kommandoradsargument
        if len(sys.argv) > 1:
            filepath = sys.argv[1]  # Använd kommandoradsargument som filsökväg
        else:
            filepath = input("Ange sökväg till bildfil: ")  # Fråga efter filsökväg
        
        print(f"Laddar upp bild: {filepath}")
        
        # Ladda upp bilden till Imgur
        image_url, error = upload_to_imgur(filepath)
        
        if error:
            print(f"Fel vid uppladdning: {error}")
            sys.exit(1)
            
        # Fråga om användaren vill spara till databasen
        save_to_db = input("Vill du spara denna bild till databasen? (y/n): ")
        
        if save_to_db.lower() == 'y':
            target_type = input("Ange måltyp (completed_route/user_profile): ")
            
            with app.app_context():
                if target_type == 'completed_route':
                    user_id = int(input("Ange användar-ID: "))
                    route_id = int(input("Ange rutt-ID: "))
                    flash_input = input("Flash? (y/n): ")
                    flash = flash_input.lower() == 'y'
                    
                    result, error = post_img_to_db(
                        image_url,
                        target_type='completed_route',
                        target_id=None,
                        user_id=user_id,
                        route_id=route_id,
                        flash=flash
                    )
                
                elif target_type == 'user_profile':
                    user_id = int(input("Ange användar-ID: "))
                    
                    result, error = post_img_to_db(
                        image_url,
                        target_type='user_profile',
                        target_id=user_id
                    )
                
                else:
                    print("Ogiltig måltyp.")
                    sys.exit(1)
                
                if error:
                    print(f"Fel: {error}")
                else:
                    print(f"Bilden har sparats: {result}")
                
    except ImportError as e:
        print(f"Fel vid import av Flask-appen: {e}")
        print("\nDetta skript måste köras från projektets rot eller i Flask-applikationens kontext.")
        print("Försök köra det med: python -m controllers.image_controller")
    except Exception as e:
        print(f"Fel: {e}")