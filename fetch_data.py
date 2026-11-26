"""Fetches standings, schedule, form, results and point leaders from the NHL and saves them as JSON in data/.

Run from the project folder: python3 fetch_data.py
"""
import json
import time
import urllib.request

API = "https://api-web.nhle.com/v1"


def fetch(path):
    request = urllib.request.Request(API + path, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def save(name, data):
    with open(f"data/{name}", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=1)


def trim_team(team):
    return {field: team[field] for field in ("abbrev", "placeName", "commonName")}


def trim_schedule(schedule):
    """Keep only what the page uses. Odds and links to betting sites are dropped."""
    return {
        "gameWeek": [
            {
                "date": day["date"],
                "games": [
                    {
                        "id": game["id"],
                        "startTimeUTC": game["startTimeUTC"],
                        "gameScheduleState": game["gameScheduleState"],
                        "homeTeam": trim_team(game["homeTeam"]),
                        "awayTeam": trim_team(game["awayTeam"]),
                    }
                    for game in day["games"]
                ],
            }
            for day in schedule["gameWeek"]
        ]
    }


def get_result(game, team):
    """W = win, L = loss, OT = loss in overtime or shootout."""
    is_home = game["homeTeam"]["abbrev"] == team
    own = game["homeTeam"] if is_home else game["awayTeam"]
    opponent = game["awayTeam"] if is_home else game["homeTeam"]
    if own["score"] > opponent["score"]:
        return "W"
    return "L" if game["gameOutcome"]["lastPeriodType"] == "REG" else "OT"


def get_outcome(game):
    """1X2 after regulation time: winner's abbreviation, or TIE if the game went to overtime or shootout."""
    if game["gameOutcome"]["lastPeriodType"] != "REG":
        return "TIE"
    home, away = game["homeTeam"], game["awayTeam"]
    return home["abbrev"] if home["score"] > away["score"] else away["abbrev"]


def fetch_form_and_results(standings):
    form = {}
    results = {}  # game id -> outcome. Each game shows up for both teams, which is fine.
    for team in (row["teamAbbrev"]["default"] for row in standings["standings"]):
        games = fetch(f"/club-schedule-season/{team}/now")["games"]
        # gameType 2 = regular season, 3 = playoffs. OFF and FINAL = finished.
        finished = [g for g in games if g["gameType"] in (2, 3) and g["gameState"] in ("OFF", "FINAL")]
        finished.sort(key=lambda g: g["startTimeUTC"])
        regular = [g for g in finished if g["gameType"] == 2]
        form[team] = [get_result(g, team) for g in regular[-5:]]  # oldest first
        for game in finished:
            results[str(game["id"])] = get_outcome(game)
        time.sleep(0.2)  # be kind to the API
    return form, dict(sorted(results.items()))


def fetch_leaders():
    """Top 5 in points, plus a large action photo of the leader for the top of the page.
    The page shows the images straight from the NHL's servers. Nothing is downloaded to the repo."""
    data = fetch("/skater-stats-leaders/current?categories=points&limit=5")
    fields = ("id", "firstName", "lastName", "sweaterNumber", "headshot", "teamAbbrev", "position", "value")
    players = [{field: player[field] for field in fields} for player in data["points"]]
    hero_image = fetch(f"/player/{players[0]['id']}/landing").get("heroImage") if players else None
    return {"points": players, "heroImage": hero_image}


# Fetch everything first, then save. If something fails, the old files are kept.
standings = fetch("/standings/now")
schedule = trim_schedule(fetch("/schedule/now"))
form, results = fetch_form_and_results(standings)
leaders = fetch_leaders()

save("standings.json", standings)
save("schedule.json", schedule)
save("form.json", form)
save("results.json", results)
save("leaders.json", leaders)
print("Saved standings, schedule and form for", len(form), "teams,", len(results), "results and", len(leaders["points"]), "point leaders")
