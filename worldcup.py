import json
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path


GROUPS = {
    "A": ["Mexico", "South Africa", "South Korea", "Czechia"],
    "B": ["Canada", "Bosnia and Herzegovina", "Qatar", "Switzerland"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["USA", "Paraguay", "Australia", "Turkiye"],
    "E": ["Germany", "Curacao", "Ivory Coast", "Ecuador"],
    "F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Iraq", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "Congo DR", "Uzbekistan", "Colombia"],
    "L": ["England", "Croatia", "Ghana", "Panama"],
}

FLAGS = {
    "Mexico": "🇲🇽", "South Africa": "🇿🇦", "South Korea": "🇰🇷", "Czechia": "🇨🇿",
    "Canada": "🇨🇦", "Bosnia and Herzegovina": "🇧🇦", "Qatar": "🇶🇦", "Switzerland": "🇨🇭",
    "Brazil": "🇧🇷", "Morocco": "🇲🇦", "Haiti": "🇭🇹", "Scotland": "🏴",
    "USA": "🇺🇸", "Paraguay": "🇵🇾", "Australia": "🇦🇺", "Turkiye": "🇹🇷",
    "Germany": "🇩🇪", "Curacao": "🇨🇼", "Ivory Coast": "🇨🇮", "Ecuador": "🇪🇨",
    "Netherlands": "🇳🇱", "Japan": "🇯🇵", "Sweden": "🇸🇪", "Tunisia": "🇹🇳",
    "Belgium": "🇧🇪", "Egypt": "🇪🇬", "Iran": "🇮🇷", "New Zealand": "🇳🇿",
    "Spain": "🇪🇸", "Cape Verde": "🇨🇻", "Saudi Arabia": "🇸🇦", "Uruguay": "🇺🇾",
    "France": "🇫🇷", "Senegal": "🇸🇳", "Iraq": "🇮🇶", "Norway": "🇳🇴",
    "Argentina": "🇦🇷", "Algeria": "🇩🇿", "Austria": "🇦🇹", "Jordan": "🇯🇴",
    "Portugal": "🇵🇹", "Congo DR": "🇨🇩", "Uzbekistan": "🇺🇿", "Colombia": "🇨🇴",
    "England": "🏴", "Croatia": "🇭🇷", "Ghana": "🇬🇭", "Panama": "🇵🇦",
}

HOSTS = [
    {"stadium": "Estadio Azteca", "city": "Mexico City", "country": "Mexico", "image": "https://images.unsplash.com/photo-1518638150340-f706e86654de?auto=format&fit=crop&w=900&q=80"},
    {"stadium": "BMO Field", "city": "Toronto", "country": "Canada", "image": "https://images.unsplash.com/photo-1517090504586-fde19ea6066f?auto=format&fit=crop&w=900&q=80"},
    {"stadium": "SoFi Stadium", "city": "Los Angeles", "country": "USA", "image": "https://images.unsplash.com/photo-1534190760961-74e8c1c5c3da?auto=format&fit=crop&w=900&q=80"},
    {"stadium": "MetLife Stadium", "city": "New York/New Jersey", "country": "USA", "image": "https://images.unsplash.com/photo-1485871981521-5b1fd3805eee?auto=format&fit=crop&w=900&q=80"},
    {"stadium": "AT&T Stadium", "city": "Dallas", "country": "USA", "image": "https://images.unsplash.com/photo-1546549032-9571cd6b27df?auto=format&fit=crop&w=900&q=80"},
    {"stadium": "BC Place", "city": "Vancouver", "country": "Canada", "image": "https://images.unsplash.com/photo-1560814304-4f05b62af116?auto=format&fit=crop&w=900&q=80"},
    {"stadium": "Hard Rock Stadium", "city": "Miami", "country": "USA", "image": "https://images.unsplash.com/photo-1506966953602-c20cc11f75e3?auto=format&fit=crop&w=900&q=80"},
    {"stadium": "Estadio BBVA", "city": "Monterrey", "country": "Mexico", "image": "https://images.unsplash.com/photo-1585464231875-d9ef1f5ad396?auto=format&fit=crop&w=900&q=80"},
]

ROUNDS = ["Dieciseisavos", "Octavos", "Cuartos", "Semifinales", "Tercer puesto", "Final"]


class WorldCupService:
    def __init__(self):
        self.db_path = Path(__file__).resolve().parents[1] / "database" / "worldcup.json"
        if not self.db_path.exists():
            self.reset()

    def reset(self):
        state = {
            "groups": deepcopy(GROUPS),
            "matches": self._generate_group_matches(),
            "playoffs": [],
            "champion": None,
            "third_place": None,
            "mvp": None,
            "scorers": {},
        }
        self._save(state)
        return {"message": "Torneo reiniciado", "summary": self.summary(state)}

    def summary(self, state=None):
        state = state or self._load()
        played = len([m for m in state["matches"] + state["playoffs"] if m.get("played")])
        total = len(state["matches"]) + len(state["playoffs"])
        goals = sum((m.get("home_goals") or 0) + (m.get("away_goals") or 0) for m in state["matches"] + state["playoffs"])
        return {
            "teams": 48,
            "groups": 12,
            "played": played,
            "total_matches": total,
            "goals": goals,
            "champion": state.get("champion"),
            "mvp": state.get("mvp"),
        }

    def get_groups(self):
        state = self._load()
        return [{"group": key, "teams": [self._team(team) for team in teams]} for key, teams in state["groups"].items()]

    def get_matches(self):
        return self._load()["matches"]

    def get_playoffs(self):
        state = self._load()
        if not state["playoffs"]:
            standings = self.get_standings()
            if self._group_stage_finished(state) and len(self._qualified_teams(standings)) == 32:
                state["playoffs"] = self._generate_round("Dieciseisavos", self._qualified_teams(standings), "P")
                self._save(state)
        return state["playoffs"]

    def save_result(self, match_id, home_goals, away_goals, penalties_home=None, penalties_away=None):
        state = self._load()
        match = self._find_match(state, match_id)
        match["home_goals"] = home_goals
        match["away_goals"] = away_goals
        match["played"] = True
        if match.get("round") != "Grupo" and home_goals == away_goals:
            match["extra_time"] = True
            if penalties_home is None or penalties_away is None or penalties_home == "" or penalties_away == "":
                raise ValueError("En playoffs, si hay empate tenes que cargar los penales.")
            home_penalties = int(penalties_home)
            away_penalties = int(penalties_away)
            if home_penalties == away_penalties:
                raise ValueError("Los penales no pueden terminar empatados.")
            match["penalties"] = {"home": home_penalties, "away": away_penalties}
        else:
            match["extra_time"] = False
            match["penalties"] = None
        match["winner"] = self._winner(match)
        if match.get("round") != "Grupo":
            self._complete_playoff_if_needed(state)
        elif self._group_stage_finished(state) and not state["playoffs"]:
            standings = self.get_standings_from_state(state)
            state["playoffs"] = self._generate_round("Dieciseisavos", self._qualified_teams(standings), "P")
        self._recalculate_scorers(state)
        if state.get("champion"):
            state["mvp"] = self._pick_mvp(state)
        self._save(state)
        return {"message": "Resultado guardado", "match": match, "summary": self.summary(state)}

    def get_standings(self):
        state = self._load()
        tables = {}
        for group, teams in state["groups"].items():
            table = {team: self._empty_row(team, group) for team in teams}
            for match in state["matches"]:
                if match["group"] != group or not match["played"]:
                    continue
                self._apply_match(table, match)
            tables[group] = sorted(table.values(), key=lambda x: (x["points"], x["gd"], x["gf"], x["wins"]), reverse=True)
        return tables

    def get_stats(self):
        state = self._load()
        matches = state["matches"] + state["playoffs"]
        played = [m for m in matches if m.get("played")]
        goals = sum((m.get("home_goals") or 0) + (m.get("away_goals") or 0) for m in played)
        top_scorers = sorted(state.get("scorers", {}).items(), key=lambda item: item[1], reverse=True)[:10]
        return {
            "summary": self.summary(state),
            "average_goals": round(goals / len(played), 2) if played else 0,
            "top_scorers": [{"player": name, "goals": goals} for name, goals in top_scorers],
            "champion": state.get("champion"),
            "third_place": state.get("third_place"),
        }

    def get_standings_from_state(self, state):
        current = self._load()
        self._save(state)
        tables = self.get_standings()
        self._save(current)
        return tables

    def _generate_group_matches(self):
        matches = []
        start = date(2026, 6, 11)
        number = 1
        for group, teams in GROUPS.items():
            pairings = [(0, 1), (2, 3), (0, 2), (1, 3), (0, 3), (1, 2)]
            for local, away in pairings:
                host = HOSTS[(number - 1) % len(HOSTS)]
                matches.append({
                    "id": f"G{number}",
                    "round": "Grupo",
                    "group": group,
                    "date": str(start + timedelta(days=(number - 1) // 4)),
                    "home": self._team(teams[local]),
                    "away": self._team(teams[away]),
                    "host": host,
                    "home_goals": None,
                    "away_goals": None,
                    "played": False,
                    "winner": None,
                })
                number += 1
        return matches

    def _generate_round(self, round_name, teams, prefix):
        matches = []
        for index in range(0, len(teams), 2):
            host = HOSTS[(index // 2) % len(HOSTS)]
            matches.append({
                "id": f"{prefix}{len(matches) + 1}",
                "round": round_name,
                "group": None,
                "date": str(date(2026, 6, 28) + timedelta(days=len(matches))),
                "home": self._team(teams[index]),
                "away": self._team(teams[index + 1]),
                "host": host,
                "home_goals": None,
                "away_goals": None,
                "extra_time": False,
                "penalties": None,
                "played": False,
                "winner": None,
            })
        return matches

    def _complete_playoff_if_needed(self, state):
        for round_index, round_name in enumerate(["Dieciseisavos", "Octavos", "Cuartos", "Semifinales"]):
            current_round = [m for m in state["playoffs"] if m["round"] == round_name]
            if not current_round or not all(m.get("played") for m in current_round):
                return

            if round_name == "Semifinales":
                if not any(m["round"] == "Tercer puesto" for m in state["playoffs"]):
                    losers = [self._loser(match) for match in current_round]
                    state["playoffs"].append(self._generate_round("Tercer puesto", losers, "TP")[0])
                if not any(m["round"] == "Final" for m in state["playoffs"]):
                    winners = [match["winner"] for match in current_round]
                    state["playoffs"].append(self._generate_round("Final", winners, "F")[0])
                break

            next_round_name = ["Octavos", "Cuartos", "Semifinales"][round_index]
            if not any(m["round"] == next_round_name for m in state["playoffs"]):
                winners = [match["winner"] for match in current_round]
                state["playoffs"].extend(self._generate_round(next_round_name, winners, f"P{round_index + 1}"))

        third_place = [m for m in state["playoffs"] if m["round"] == "Tercer puesto" and m.get("played")]
        finals = [m for m in state["playoffs"] if m["round"] == "Final" and m.get("played")]
        if third_place:
            state["third_place"] = third_place[-1]["winner"]
        if finals:
            state["champion"] = finals[-1]["winner"]
            state["mvp"] = self._pick_mvp(state)

    def _qualified_teams(self, standings):
        first_second = []
        thirds = []
        for group in sorted(standings):
            rows = standings[group]
            first_second.extend([rows[0]["team"], rows[1]["team"]])
            thirds.append(rows[2])
        best_thirds = sorted(thirds, key=lambda x: (x["points"], x["gd"], x["gf"]), reverse=True)[:8]
        qualified = first_second + [row["team"] for row in best_thirds]
        return qualified[:32]

    def _apply_match(self, table, match):
        home = match["home"]["name"]
        away = match["away"]["name"]
        hg = match["home_goals"]
        ag = match["away_goals"]
        table[home]["played"] += 1
        table[away]["played"] += 1
        table[home]["gf"] += hg
        table[home]["ga"] += ag
        table[away]["gf"] += ag
        table[away]["ga"] += hg
        if hg > ag:
            table[home]["wins"] += 1
            table[away]["losses"] += 1
            table[home]["points"] += 3
        elif ag > hg:
            table[away]["wins"] += 1
            table[home]["losses"] += 1
            table[away]["points"] += 3
        else:
            table[home]["draws"] += 1
            table[away]["draws"] += 1
            table[home]["points"] += 1
            table[away]["points"] += 1
        table[home]["gd"] = table[home]["gf"] - table[home]["ga"]
        table[away]["gd"] = table[away]["gf"] - table[away]["ga"]

    def _winner(self, match):
        if match["home_goals"] is None:
            return None
        if match["home_goals"] > match["away_goals"]:
            return match["home"]["name"]
        if match["away_goals"] > match["home_goals"]:
            return match["away"]["name"]
        penalties = match.get("penalties")
        if penalties:
            return match["home"]["name"] if penalties["home"] > penalties["away"] else match["away"]["name"]
        return "Empate" if match.get("round") == "Grupo" else None

    def _loser(self, match):
        return match["away"]["name"] if match["winner"] == match["home"]["name"] else match["home"]["name"]

    def _empty_row(self, team, group):
        return {"team": team, "flag": FLAGS.get(team, "🏳️"), "group": group, "points": 0, "played": 0, "wins": 0, "draws": 0, "losses": 0, "gf": 0, "ga": 0, "gd": 0}

    def _team(self, name):
        return {"name": name, "flag": FLAGS.get(name, "🏳️")}

    def _add_scorers(self, state, match):
        if not match.get("played"):
            return
        for side in ["home", "away"]:
            goals = match.get(f"{side}_goals") or 0
            team = match[side]["name"]
            for index in range(goals):
                player = f"{team} Jugador {index + 1}"
                state["scorers"][player] = state["scorers"].get(player, 0) + 1

    def _recalculate_scorers(self, state):
        state["scorers"] = {}
        for match in state["matches"] + state["playoffs"]:
            self._add_scorers(state, match)

    def _pick_mvp(self, state):
        if not state.get("scorers"):
            return None
        return max(state["scorers"], key=state["scorers"].get)

    def _group_stage_finished(self, state):
        return all(match.get("played") for match in state["matches"])

    def _find_match(self, state, match_id):
        for match in state["matches"] + state["playoffs"]:
            if match["id"] == match_id:
                return match
        raise ValueError("Partido no encontrado")

    def _load(self):
        return json.loads(self.db_path.read_text(encoding="utf-8"))

    def _save(self, state):
        self.db_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
