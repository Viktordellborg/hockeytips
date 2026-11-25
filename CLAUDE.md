# CLAUDE.md – Hockeytips

## Vad det här är
En hemsida som visar NHL-tabellen, kommande matcher och enkla tips baserade på statistik.
Bara för skojs skull, inga riktiga spelpengar. Målet är både att bygga och att lära mig under tiden.
Jag kan grundläggande Java, C#, databaser, VS Code och GitHub.

## Så här arbetar vi
- Svara på svenska, kort och rakt. Kod, filnamn och commit-meddelanden på engelska.
- Förklara medan du bygger: vad du gör, varför du väljer just den lösningen och vad nya begrepp betyder. Håll det kort och konkret.
- Föreslå hellre en enkel lösning som fungerar än en avancerad.
- Bygg i små steg. Kör och testa efter varje steg innan du går vidare.
- Fråga innan du lägger till nya beroenden, ändrar mappstrukturen eller tar bort filer.
- Lägg aldrig lösenord, API-nycklar eller annat hemligt i koden eller i Git. Använd en .env-fil som ligger i .gitignore. Repot är publikt.
- När något fungerar: föreslå en commit med ett kort meddelande. Jag gör commit och push själv.

## Var saker ligger
- index.html: sidan, med CSS och JavaScript
- data/: JSON från NHL, skrivs av fetch_data.py
- fetch_data.py: hämtar tabell, schema och form (bara Pythons standardbibliotek)
- .github/workflows/fetch-data.yml: kör skriptet enligt schema, sparar ändringarna och bygger om sidan
- README.md: beskrivning och plan
- IDEER.md: idéer som inte är byggda än

## Köra och testa
- Hämta ny data: `python3 fetch_data.py`
- Visa sidan: `python3 -m http.server 8000` och öppna http://localhost:8000
- Hämta från GitHub (pull) innan du ändrar något, eftersom Actions också gör commits.
- Sidan publiceras från main på https://viktordellborg.github.io/hockeytips/

## Namn
- Små bokstäver med bindestreck för nya filer. Python-filer får ha understreck.
- Datum skrivs ÅÅÅÅ-MM-DD.
- Commits före 2026-11-26 är delvis på svenska. De får vara kvar.
