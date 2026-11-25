"""Hämtar varje lags senaste 5 matcher och sparar dem i data/form.json.

Kör från projektmappen: python3 hamta_form.py
"""
import json
import time
import urllib.request

API = "https://api-web.nhle.com/v1"


def hamta(adress):
    fraga = urllib.request.Request(API + adress, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(fraga, timeout=20) as svar:
        return json.load(svar)


def resultat(match, lag):
    """V = vinst, F = förlust, Ö = förlust efter förlängning eller straffar."""
    hemma = match["homeTeam"]["abbrev"] == lag
    vi = match["homeTeam"] if hemma else match["awayTeam"]
    de = match["awayTeam"] if hemma else match["homeTeam"]
    if vi["score"] > de["score"]:
        return "V"
    return "F" if match["gameOutcome"]["lastPeriodType"] == "REG" else "Ö"


with open("data/standings.json", encoding="utf-8") as fil:
    lagen = [lag["teamAbbrev"]["default"] for lag in json.load(fil)["standings"]]

form = {}
for lag in lagen:
    matcher = hamta(f"/club-schedule-season/{lag}/now")["games"]
    # gameType 2 = grundserie. OFF och FINAL = färdigspelad.
    klara = [m for m in matcher if m["gameType"] == 2 and m["gameState"] in ("OFF", "FINAL")]
    klara.sort(key=lambda m: m["startTimeUTC"])
    form[lag] = [resultat(m, lag) for m in klara[-5:]]  # äldst först
    time.sleep(0.2)  # var snäll mot API:et

with open("data/form.json", "w", encoding="utf-8") as fil:
    json.dump(form, fil, ensure_ascii=False, indent=1)
print("Sparade form för", len(form), "lag")
