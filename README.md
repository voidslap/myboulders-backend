# myboulders-backend

## Produktbeskrivning
MyBoulders är en tränings- och social plattform för klättringsentusiaster. Applikationen låter användare logga sina klättringsrutter, sätta personliga mål, följa sina framsteg och interagera med andra klättrare. Funktioner inkluderar en leaderboard för att visa toppklättrare, användarprofiler med prestationer och statistik, samt en dashboard för att få en översikt över användarens klättringsdata.

## Installation och start

### Backend
1. **Krav**: 
    Python 3.12 eller senare

2. **(Valfritt men rekommenderat)**
    Skapa en lokal mapp på din dator där du kan klona ner båda repos, döp en till frontend och en till backend.

3. **Klona backend**:
    git clone <repo-url>  
    cd myboulders-backend

4. **Installera Python-paket**:
    pip install -r requirements.txt 

5. **Starta backend servern**:
    python app.py

## Miljövariabler
Skapa en `.env`-fil i projektets rot med följande variabler: 

**Hemlig nyckel**: (för t.ex. sessions eller JWT – beroende på implementation)  
`SECRET_KEY = din hemliga nyckel`

### Frontend
1. **Krav**:    
    Node.js 18 eller senare.

2. **Klona frontend**:
    git clone <repo-url>  
    cd myboulders-frontend

3. **Installera Node-paket**:
    npm install

4. **Starta frontend servern**:
    npm run dev

5. **Öppna applikationen**:
    Klicka via terminalen eller besök http://localhost:5173

## Grafisk profil

### Färger
**Bakgrund**: #121212 (mörkgrå)  
**Primärfärg**: #7ea685 (mossgrön)  
**Sekundärfärg**: #a67d5b (jordbrun)  
**Accentfärg**: #c9a66b (sandfärgad)

### Typsnitt
**Primärt typsnitt**: System-ui, Roboto, sans-serif.

### Designprinciper
Vi har valt ett färgschema som inspirerats av naturmaterial – jord, sten, mossa och sand – eftersom klättring är en naturnära aktivitet. Designen är minimalistisk och fokuserar på att låta innehållet stå i centrum. Vi använder tydliga färgkontraster för läsbarhet, responsiva komponenter för alla enheter och inspiration från material design för ett modernt och tillgängligt gränssnitt.

## Autentisering
Applikationen använder JWT (JSON Web Tokens) för att autentisera användare. Tokens sparas i `HttpOnly` cookies för att skydda mot XSS-attacker. Skyddade routes använder `@auth_required`-dekoration för att enkelt säkra åtkomst. Inloggning krävs för att komma åt användarens dashboard och mål.

## Tester och CI
Gruppen har tillsammans genomfört tester med hjälp av **Pytest** för flera delar av applikationen, inklusive användarregistrering, inloggning, databasoperationer och CRUD-funktionalitet. Tester körs lokalt och kan utökas med GitHub Actions vid behov.

## Branchstruktur

**main**: Stabil kod som är redo för produktion  
**dev**: Aktiv utvecklingsbranch där nya funktioner testas  
**feature/**: Skapas för specifika funktioner eller buggar, t.ex. `feature/login`

### Arbetsflöde

1. Skapa ny feature branch från dev  
2. Gör ändringar och testa lokalt  
3. Skicka en pull request (PR) till dev  

## PR-regler

1. Alla PRs måste granskas av minst två gruppmedlemmar innan de slås samman  
2. PRs ska inkludera en tydlig beskrivning av ändringarna  
3. Commits ska vara beskrivande och i imperativ form, t.ex. "Add login feature"

## Individuella undersidor
Varje gruppmedlem ansvarar för en egen undersida i applikationen (t.ex. `/my-progress`, `/upload-route`) där de demonstrerar koppling mellan frontend och backend med minst två olika typer av HTTP-förfrågningar, t.ex. GET och POST.

## Databasstruktur
MyBoulders Database Structure

## Users

id (Integer, PK, autoincrement)

username (String, NOT NULL, UNIQUE)

hashed_password (String, NOT NULL)

email (String, NOT NULL, UNIQUE)

profile_image_url (String, NOT NULL)

register_date (DateTime, NOT NULL, DEFAULT now)

## Routes
id (Integer, PK, autoincrement)

difficulty_id (Integer, FK, NOT NULL)

type (String, NOT NULL)

## Difficulty Levels
id (Integer, PK, autoincrement)

grade (String, NOT NULL)

## Completed Routes
id (Integer, PK, autoincrement)

user_id (Integer, FK, NOT NULL)

route_id (Integer, FK, NOT NULL)

flash (Boolean, NOT NULL)

date (DateTime, NOT NULL, DEFAULT now)

image_url (String, NULL)

## Achievements
id (Integer, PK, autoincrement)

user_id (Integer, FK, NOT NULL)

achievement_name (String, NOT NULL)

achievement_date (DateTime, NOT NULL, DEFAULT now)

## Goals
id (Integer, PK, autoincrement)

user_id (Integer, FK, NOT NULL)

title (String, NOT NULL)

description (Text, NULL)

target_grade (String, NULL)

deadline (DateTime, NULL)

completed (Boolean, DEFAULT FALSE)

completed_date (DateTime, NULL)

created_at (DateTime, DEFAULT now)

updated_at (DateTime, DEFAULT now)


## Kända buggar / Kommande funktioner

- Inloggade användare kan fortfarande nå `/login` och `/register` som om de vore utloggade  
- Kommande funktion: möjligheten att kommentera på andras rutter  
- Kommande funktion: bättre validering av bildformat vid uppladdning


## Mall till .env fil:
DATABASE_URL=

IMGUR_CLIENT_ID=

IMGUR_CLIENT_SECRET=

IMGUR_USERNAME=

IMGUR_PASSWORD=

SECRET_KEY=
