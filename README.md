# Hockeytips

En liten hemsida som visar NHL-matcher och enkla tips baserade på statistik.
Bara för skojs skull, inga riktiga spelpengar.

## Så fungerar det (planerat)

1. GitHub Actions hämtar data från `https://api-web.nhle.com` enligt schema och sparar den som JSON i `data/`.
2. Sidan (HTML, CSS och JavaScript) läser JSON-filerna och räknar ut ett tips per match.
3. GitHub Pages publicerar sidan.

NHL:s API svarar utan CORS-tillstånd, så webbläsaren får inte läsa det direkt från vår sida.
Därför hämtas datan i steg 1 i stället. API:et är gratis och kräver ingen nyckel, men är
inofficiellt dokumenterat och kan ändras.

## API-adresser

| Adress | Innehåll |
| --- | --- |
| `/v1/standings/now` | Tabellen, samt form senaste 10 matcherna |
| `/v1/schedule/now` | Matcher den kommande veckan |
| `/v1/club-schedule-season/TOR/now` | Ett lags säsong med resultat, för senaste 5 matcherna |

`/now` skickar vidare till en adress med datum, så använd `curl -L`.

## Plan

- [x] 1. Repo på GitHub
- [x] 2. Hämta tabellen en gång till `data/standings.json` och visa den på en sida
- [x] 3. Publicera på GitHub Pages
- [x] 4. Visa kommande matcher
- [ ] 5. Räkna form (senaste 5) och visa ett tips per match
- [ ] 6. Hämta ny data automatiskt med GitHub Actions
- [ ] 7. Putsa designen och mobilvyn
