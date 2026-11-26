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
- [x] 5. Räkna form (senaste 5) och visa ett tips per match
- [x] 6. Hämta ny data automatiskt med GitHub Actions
- [x] 7. Putsa designen och mobilvyn

## Plan: tippningsliga med Supabase

Supabase ger en Postgres-databas och inloggning. Sidan pratar direkt med Supabase från webbläsaren.
Nyckeln i sidan (publishable/anon) är offentlig. Säkerheten kommer från Row Level Security (RLS)
på varje tabell. Den hemliga nyckeln (service_role/secret) ska aldrig in i repot.

- [x] 1. Koppla sidan till Supabase-projektet
- [x] 2. Inloggning med e-post
- [ ] 3. Tabeller för ligor, medlemmar och tips, med RLS
- [x] 4. Tippa på matcher innan de startar
- [ ] 5. Skapa en liga och bjud in med en kod
- [ ] 6. Poäng och topplista
