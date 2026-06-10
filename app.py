from flask import Flask, render_template, redirect, url_for, request
from services.worldcup import WorldCupService


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    service = WorldCupService()

    @app.route("/")
    def index():
        return render_template("index.html", summary=service.get_summary())

    @app.route("/groups")
    def groups():
        groups = service.get_groups()
        standings = service.get_all_group_standings()
        matches = service.get_matches()
        matches_by_group = {g: [m for m in matches if m['group'] == g] for g in groups}
        team_map = {t['id']: t['name'] for t in service._data['teams']}
        team_map_full = {t['id']: t for t in service._data['teams']}
        return render_template("groups.html", groups=groups, standings=standings, matches=matches, matches_by_group=matches_by_group, team_map=team_map, team_map_full=team_map_full)

    @app.route("/matches/<match_id>/result", methods=["POST"])
    def save_result(match_id):
        home_goals = request.form.get('home_goals', '')
        away_goals = request.form.get('away_goals', '')
        if home_goals == '' and away_goals == '':
            return redirect(request.referrer or url_for('groups'))
        try:
            hg = int(home_goals) if home_goals != '' else 0
            ag = int(away_goals) if away_goals != '' else 0
        except ValueError:
            hg, ag = 0, 0
        service.save_result(match_id, hg, ag)
        return redirect(request.referrer or url_for('groups'))

    @app.route("/matches/<match_id>/reset", methods=["POST"])
    def reset_match(match_id):
        service.reset_match(match_id)
        return redirect(request.referrer or url_for('groups'))

    @app.route("/playoffs")
    def playoffs():
        bracket = service.get_playoffs()
        team_map = {t['id']: t['name'] for t in service._data['teams']}
        team_map_full = {t['id']: t for t in service._data['teams']}
        return render_template("playoffs.html", bracket=bracket, team_map=team_map, team_map_full=team_map_full)

    @app.route("/teams")
    def teams():
        # listar las 48 selecciones con datos completos
        teams = service._data['teams']
        return render_template('teams.html', teams=teams)

    @app.route("/simulate", methods=["POST"])
    def simulate():
        service.simulate_worldcup()
        return redirect(url_for('stats'))

    @app.route("/stats")
    def stats():
        stats = service.get_stats()
        team_map = {t['id']: t['name'] for t in service._data['teams']}
        team_map_full = {t['id']: t for t in service._data['teams']}
        return render_template("stats.html", stats=stats, team_map=team_map, team_map_full=team_map_full)

    @app.route("/reset", methods=["POST"])
    def reset_all():
        service.reset_all()
        return redirect(url_for('index'))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=False, port=5000)
