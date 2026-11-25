"""Hämtar tabell, schema och form från NHL och sparar dem som JSON i data/.

Kör från projektmappen: python3 hamta_data.py
"""
import json
import time
import urllib.request

API = "https://api-web.nhle.com/v1"


def hamta(adress):
    fraga = urllib.request.Request(API + adress, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(fraga, timeout=20) as svar:
        return json.load(svar)


def spara(namn, data):
    with open(f"data/{namn}", "w", encoding="utf-8") as fil:
        json.dump(data, fil, ensure_ascii=False, indent=1)


def lag_i_korthet(lag):
    return {falt: lag[falt] for falt in ("abbrev", "placeName", "commonName")}


def rensa_schema(schema):
    """Behåll bara det sidan använder. Odds och länkar till spelbolag följer inte med."""
    return {
        "gameWeek": [
            {
                "date": dag["date"],
                "games": [
                    {
                        "id": m["id"],
                        "startTimeUTC": m["startTimeUTC"],
                        "gameScheduleState": m["gameScheduleState"],
                        "homeTeam": lag_i_korthet(m["homeTeam"]),
                        "awayTeam": lag_i_korthet(m["awayTeam"]),
                    }
                    for m in dag["games"]
                ],
            }
            for dag in schema["gameWeek"]
        ]
    }


def resultat(match, lag):
    """V = vinst, F = förlust, Ö = förlust efter förlängning eller straffar."""
    hemma = match["homeTeam"]["abbrev"] == lag
    vi = match["homeTeam"] if hemma else match["awayTeam"]
    de = match["awayTeam"] if hemma else match["homeTeam"]
    if vi["score"] > de["score"]:
        return "V"
    return "F" if match["gameOutcome"]["lastPeriodType"] == "REG" else "Ö"


def hamta_form(tabell):
    form = {}
    for lag in (rad["teamAbbrev"]["default"] for rad in tabell["standings"]):
        matcher = hamta(f"/club-schedule-season/{lag}/now")["games"]
        # gameType 2 = grundserie. OFF och FINAL = färdigspelad.
        klara = [m for m in matcher if m["gameType"] == 2 and m["gameState"] in ("OFF", "FINAL")]
        klara.sort(key=lambda m: m["startTimeUTC"])
        form[lag] = [resultat(m, lag) for m in klara[-5:]]  # äldst först
        time.sleep(0.2)  # var snäll mot API:et
    return form


# Hämta allt först och spara sedan. Om något går fel ligger de gamla filerna kvar.
tabell = hamta("/standings/now")
schema = rensa_schema(hamta("/schedule/now"))
form = hamta_form(tabell)

spara("standings.json", tabell)
spara("schedule.json", schema)
spara("form.json", form)
print("Sparade tabell, schema och form för", len(form), "lag")
