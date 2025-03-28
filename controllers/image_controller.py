import os
import sys
import requests
import base64
from dotenv import load_dotenv

# Add the project root to Python path for proper imports
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from config.db_config import db
from models.completed_routes_model import CompletedRoute
from models.users_model import User


load_dotenv()

# Imgur API credentials
IMGUR_CLIENT_ID = os.getenv('IMGUR_CLIENT_ID')
IMGUR_API_URL = 'https://api.imgur.com/3/image'
IMGUR_CLIENT_SECRET = os.getenv('IMGUR_CLIENT_SECRET')


def upload_to_imgur(filepath):
    """
    Ladda upp en bild till Imgur och få direktlänk till bilden
    
    Args:
        filepath (str): Sökväg till bildfilen som ska laddas upp
        
    Returns:
        tuple: (direktlänk till bilden, felmeddelande eller None)
    """
    try:
        # Kontrollera om filen finns
        if not os.path.exists(filepath):
            return None, f"Filen hittades inte: {filepath}"
            
        # Läs bildfilen som binärdata
        with open(filepath, 'rb') as file:
            binary_data = file.read()
            
        # Konvertera bilden till base64
        b64_image = base64.b64encode(binary_data)
        
        # Förbereder headers för Imgur API
        headers = {
            'Authorization': f'Client-ID {IMGUR_CLIENT_ID}'
        }
        
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
                delete_hash = json_data['data']['deletehash']  # Kan vara bra att spara för framtida borttagning
                
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
            

    except ImportError as e:
        print(f"Fel vid import av Flask-appen: {e}")
        print("\nDetta skript måste köras från projektets rot eller i Flask-applikationens kontext.")
        print("Försök köra det med: python -m controllers.image_controller")
    except Exception as e:
        print(f"Fel: {e}")