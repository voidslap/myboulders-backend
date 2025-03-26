
# Git Kommando Guide

## Vanliga Git-kommandon och deras funktioner

### 1. git init
Skapar ett nytt Git-repo i den aktuella mappen.

Användning:
git init

### 2. git clone
Kopierar ett befintligt Git-repo från en fjärrserver (som GitHub) till din lokala maskin.

Användning:
git clone <repo-url>

### 3. git status
Visar statusen på filer i ditt repo (om de har ändrats, om de är staged, eller om de är redo att committas).

Användning:
git status

### 4. git add
Lägger till ändringar till staging area (så att de kan committas).

- Lägg till en fil:
  git add filnamn
- Lägg till alla ändrade filer:
  git add .

### 5. git commit
Skapar en commit (en "snapshot") av de ändringar som har lagts till staging area.

Användning:
git commit -m "Commit message"

### 6. git push
Skickar dina commits från din lokala branch till en fjärrbranch (t.ex. på GitHub).

Användning:
git push origin branch-namn

### 7. git pull
Hämtar de senaste ändringarna från fjärrrepoet och slår samman dem med din nuvarande branch.

Användning:
git pull origin branch-namn

### 8. git fetch
Hämtar de senaste ändringarna från fjärrrepoet, men slår inte ihop dem med din aktuella branch.

Användning:
git fetch

### 9. git merge
Slår samman ändringar från en annan branch till den aktuella branch du är på.

Användning:
git merge branch-namn

### 10. git branch
Visar alla brancher i ditt repo eller skapar en ny branch.

- Visa alla brancher:
  git branch
- Skapa en ny branch:
  git branch branch-namn

### 11. git checkout
Byter till en annan branch eller återställer en fil till ett tidigare tillstånd.

- Byt till en annan branch:
  git checkout branch-namn
- Återställ en fil till senaste commit:
  git checkout filnamn

### 12. git log
Visar en lista på alla commits i din nuvarande branch.

Användning:
git log

### 13. git diff
Visar skillnader mellan ändringar i filerna och senaste commit.

Användning:
git diff

### 14. git remote
Hantera fjärrrepo. Till exempel, visa fjärrrepo som är kopplade till ditt lokala repo.

- Visa fjärrrepo:
  git remote -v
- Lägg till ett nytt fjärrrepo:
  git remote add origin <repo-url>

### 15. git reset
Återställer filändringar från staging area eller senaste commit.

- Ta bort filer från staging area:
  git reset filnamn
- Återställ senaste commit (men behåll ändringar lokalt):
  git reset --soft HEAD~1

### 16. git rm
Tar bort filer från både din arbetskatalog och Git.

Användning:
git rm filnamn

### 17. git tag
Skapar en tagg (en punkt i historiken, vanligtvis för versioner).

Användning:
git tag v1.0

### 18. git push --tags
Pusha taggar till fjärrrepo.

Användning:
git push --tags

### 19. git rebase
Omarrangerar commits i din branch för att skapa en renare historia (kan användas istället för git merge).

Användning:
git rebase branch-namn

### 20. git stash
Tillfälligt sparar ändringar som inte är klara, så att du kan byta branch utan att förlora dem.

Användning:
- Stash ändringar:
  git stash
- Återställa stash:
  git stash pop

## Git Arbetsflöde: Ordning av Kommandon när du är Klar för Dagen

Här följer en logisk ordning av kommandon som du kan använda när du är klar för dagen och vill säkerställa att ditt arbete är sparat och synkat.

1. **Kontrollera status (valfritt men bra):**

   Du kan börja med att kontrollera status på dina ändringar för att veta vilka filer som har ändrats.

   ```bash
   git status
   ```

2. **Lägg till ändringar till staging area:**

   Om du har ändringar som du vill spara i din commit, lägg till dem till staging area.

   - Lägg till alla ändrade filer:
     ```bash
     git add .
     ```

3. **Skapa en commit:**

   När dina ändringar är i staging area, gör en commit för att spara dina ändringar lokalt i historiken.

   ```bash
   git commit -m "Beskrivning av ändringarna"
   ```

4. **Kontrollera om du är på rätt branch:**

   Se till att du är på rätt branch innan du pushar.

   ```bash
   git checkout branch-namn
   ```

5. **Push dina ändringar till GitHub:**

   När du är klar med att committa och är på rätt branch, skicka dina ändringar till GitHub (eller annan fjärrserver).

   ```bash
   git push origin branch-namn
   ```

6. **Hämta de senaste ändringarna (valfritt):**

   Om du vet att andra har arbetat på samma repo, kan du hämta de senaste ändringarna från GitHub.

   ```bash
   git pull origin branch-namn
   ```

7. **Stasha ändringar (valfritt):**

   Om du inte är klar med din kod men vill byta till en annan branch eller bara stänga ner arbetet för dagen, kan du stash dina ändringar tillfälligt.

   ```bash
   git stash
   ```

8. **Stäng av terminalen och logga ut:**

   Nu när dina ändringar är committade och pushade (eller stashed om du inte var klar), kan du stänga din terminal eller logga ut.
git_guide.txt
5 KB