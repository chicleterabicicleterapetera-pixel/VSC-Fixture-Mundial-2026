from flask import Blueprint, jsonify, request

from services.worldcup import WorldCupService

api = Blueprint("api", __name__, url_prefix="/api")
service = WorldCupService()


@api.get("/health")
def health():
    return jsonify({"status": "ok", "message": "API Mundial 2026 funcionando"})


@api.get("/summary")
def summary():
    return jsonify(service.summary())


@api.get("/groups")
def groups():
    return jsonify(service.get_groups())


@api.get("/matches")
def matches():
    return jsonify(service.get_matches())


@api.post("/matches/<match_id>/result")
def save_result(match_id):
    data = request.get_json() or {}
    home_goals = int(data.get("home_goals", 0))
    away_goals = int(data.get("away_goals", 0))
    penalties_home = data.get("penalties_home")
    penalties_away = data.get("penalties_away")
    try:
        return jsonify(service.save_result(match_id, home_goals, away_goals, penalties_home, penalties_away))
    except ValueError as error:
        return jsonify({"error": str(error)}), 400


@api.get("/standings")
def standings():
    return jsonify(service.get_standings())


@api.get("/playoffs")
def playoffs():
    return jsonify(service.get_playoffs())


@api.get("/stats")
def stats():
    return jsonify(service.get_stats())


@api.post("/reset")
def reset():
    return jsonify(service.reset())
