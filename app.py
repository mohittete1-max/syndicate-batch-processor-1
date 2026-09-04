import base64
import csv
import io
import os
import uuid
import requests
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Tuple, Dict, Optional

from flask import Flask, request, render_template_string, redirect, url_for
from pulp import *

# ---------- API Settings ----------
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-2.5-pro"
API_KEY = os.getenv("OX_ALPHA_KEY", "your-ox-alpha-key")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "X-Title": "Cricket DFS Optimizer (Dream11/Come11)",
}

CRICAPI_KEY = os.getenv("CRICAPI_KEY", "")
OWM_API_KEY = os.getenv("OWM_API_KEY", "")

# ---------- Platform Configuration ----------
@dataclass
class PlatformConfig:
    name: str
    salary_cap: int = 100
    team_size: int = 11
    max_per_team: int = 7
    role_min: Dict[str, int] = field(default_factory=lambda: {"WK":1, "BAT":1, "AR":1, "BOWL":1})
    role_max: Dict[str, int] = field(default_factory=lambda: {"WK":4, "BAT":6, "AR":6, "BOWL":6})
    captain_mult: float = 2.0
    vice_mult: float = 1.5

PLATFORMS = {
    "dream11": PlatformConfig(name="Dream11"),
    "come11": PlatformConfig(name="Come11"),
}

# ---------- Player Model ----------
@dataclass
class Player:
    name: str
    role: str
    salary: int
    points: float
    team: str
    ownership: Optional[float] = None

def normalize_role(raw: str) -> str:
    raw = raw.strip().upper()
    m = {"BAT":"BAT", "BATSMAN":"BAT", "BOWL":"BOWL", "BOWLER":"BOWL",
         "AR":"AR", "ALL":"AR", "ALL-ROUNDER":"AR", "WK":"WK", "KEEPER":"WK",
         "WICKETKEEPER":"WK", "WICKET-KEEPER":"WK"}
    return m.get(raw, "BAT")

# ---------- CSV Parsing ----------
def parse_csv(text: str) -> List[Player]:
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise ValueError("Empty CSV")
    hdrs = {h.strip().lower(): h for h in reader.fieldnames}

    def col(*names):
        for n in names:
            if n in hdrs:
                return hdrs[n]
        return None

    c_pos  = col("position", "pos", "role")
    c_name = col("name", "playername")
    c_sal  = col("salary", "credit", "credits", "price")
    c_pts  = col("points", "avgpointspergame", "projection", "fpts")
    c_team = col("team", "teamabbrev")
    c_own  = col("ownership", "own%", "own_pct", "exposure")

    if not (c_name and c_sal and c_pts):
        raise ValueError("CSV must have Name, Salary/Credit, and Points columns.")

    players = []
    for row in reader:
        name = row[c_name].strip()
        if not name:
            continue
        try:
            salary = int(float(row[c_sal]))
            points = float(row[c_pts])
        except:
            continue
        team = row.get(c_team, "UNK").strip() if c_team else "UNK"
        role = normalize_role(row[c_pos]) if c_pos else "BAT"
        ownership = None
        if c_own and row.get(c_own, "").strip():
            try:
                ownership = float(row[c_own].strip().replace("%", ""))
            except:
                ownership = None
        players.append(Player(name, role, salary, points, team, ownership))
    if not players:
        raise ValueError("No valid players in CSV.")
    return players

# ---------- Weather & Pitch Modifiers ----------
def apply_conditions(players: List[Player], weather: str = "clear", pitch: str = "neutral") -> List[Player]:
    multipliers = {
        ("rain", "BOWL"): 1.25,
        ("rain", "AR"): 1.1,
        ("cloudy", "BOWL"): 1.1,
        ("cloudy", "AR"): 1.05,
        ("humid", "BOWL"): 1.1,
        ("flat", "BAT"): 1.15,
        ("flat", "WK"): 1.1,
        ("flat", "AR"): 1.05,
        ("green", "BOWL"): 1.2,
        ("green", "AR"): 1.1,
        ("dusty", "BAT"): 1.1,
        ("dusty", "AR"): 1.05,
        ("dusty", "BOWL"): 1.05,
    }
    modified = []
    for p in players:
        factor = multipliers.get((weather, p.role), 1.0)
        new_points = round(p.points * factor, 1)
        modified.append(Player(p.name, p.role, p.salary, new_points, p.team, p.ownership))
    return modified

def fetch_live_weather(city: str) -> str:
    if not OWM_API_KEY or not city:
        return "clear"
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        resp = requests.get(url, params={"q": city, "appid": OWM_API_KEY, "units": "metric"}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        main = data.get("weather", [{}])[0].get("main", "").lower()
        mapping = {
            "rain": "rain", "drizzle": "rain", "thunderstorm": "rain",
            "clouds": "cloudy", "clear": "clear", "mist": "humid",
            "fog": "humid", "haze": "humid",
        }
        return mapping.get(main, "clear")
    except:
        return "clear"

# ---------- Optimizer (Incorporating Jarvis Protocols) ----------
def optimize(
    players: List[Player],
    cfg: PlatformConfig,
    max_player_own: Optional[float] = None,
    max_total_own: Optional[float] = None,
    min_player_score: float = 0,
    min_team_score: Optional[float] = None,
) -> Tuple[List[Tuple[Player, str]], float]:
    
    # ── J.A.R.V.I.S. PROTOCOL: Tactical Integrity Filter ──
    if min_player_score > 0:
        players = [p for p in players if p.points >= min_player_score]
        if len(players) < cfg.team_size:
            return [], 0.0

    n = len(players)
    x = LpVariable.dicts("x", range(n), cat="Binary")
    c = LpVariable.dicts("c", range(n), cat="Binary")
    v = LpVariable.dicts("v", range(n), cat="Binary")

    total_score_expr = (
        lpSum(x[i] * players[i].points for i in range(n))
        + lpSum(c[i] * players[i].points * (cfg.captain_mult - 1) for i in range(n))
        + lpSum(v[i] * players[i].points * (cfg.vice_mult - 1) for i in range(n))
    )

    prob = LpProblem(f"DFS_{cfg.name}", LpMaximize)
    prob += total_score_expr

    # Salary & team size limits
    prob += lpSum(x[i] * players[i].salary for i in range(n)) <= cfg.salary_cap
    prob += lpSum(x[i] for i in range(n)) == cfg.team_size

    # One captain & one vice-captain restriction
    prob += lpSum(c[i] for i in range(n)) == 1
    prob += lpSum(v[i] for i in range(n)) == 1
    for i in range(n):
        prob += c[i] <= x[i]
        prob += v[i] <= x[i]
        prob += c[i] + v[i] <= 1

    # Role constraints
    for role, mn in cfg.role_min.items():
        idxs = [i for i, p in enumerate(players) if p.role == role]
        prob += lpSum(x[i] for i in idxs) >= mn
    for role, mx in cfg.role_max.items():
        idxs = [i for i, p in enumerate(players) if p.role == role]
        prob += lpSum(x[i] for i in idxs) <= mx

    # Team stacking limits
    teams = set(p.team for p in players)
    for t in teams:
        idxs = [i for i, p in enumerate(players) if p.team == t]
        prob += lpSum(x[i] for i in idxs) <= cfg.max_per_team

    # Ownership constraints
    has_own = any(p.ownership is not None for p in players)
    if has_own and max_player_own is not None:
        for i, p in enumerate(players):
            if p.ownership is not None:
                prob += x[i] * p.ownership <= max_player_own
    if has_own and max_total_own is not None:
        prob += lpSum(x[i] * (p.ownership or 0) for i, p in enumerate(players)) <= max_total_own

    # Dream team score target constraint
    if min_team_score is not None:
        prob += total_score_expr >= min_team_score

    prob.solve(PULP_CBC_MSG(msg=0))
    if LpStatus[prob.status] != "Optimal":
        return [], 0.0

    lineup = []
    total = 0.0
    for i in range(n):
        if value(x[i]) == 1:
            desig = ""
            if value(c[i]) == 1:
                desig = "C"
            elif value(v[i]) == 1:
                desig = "VC"
            lineup.append((players[i], desig))
            total += players[i].points
            if desig == "C":
                total += players[i].points * (cfg.captain_mult - 1)
            elif desig == "VC":
                total += players[i].points * (cfg.vice_mult - 1)

    return lineup, total

# ---------- Gemini Review with Jarvis Persona ----------
def gemini_review(lineup, total_pts, platform):
    if not API_KEY or API_KEY == "your-ox-alpha-key":
        return "⚠️ Set OX_ALPHA_KEY env variable to enable J.A.R.V.I.S. analysis."
    lines = []
    for p, d in lineup:
        tag = {"C":" (Captain - 2x)","VC":" (Vice-Captain - 1.5x)","":""}[d]
        own_str = f", {p.ownership}% own" if p.ownership is not None else ""
        lines.append(f"{p.name} ({p.role}, {p.team}, {p.salary} cr, {p.points:.1f} pts{own_str}){tag}")
    text = "\n".join(lines)
    
    prompt = f"""You are J.A.R.V.I.S., an advanced tactical AI assistant managing elite fantasy cricket operations for {platform}. Analyze the following optimized XI with surgical precision:

{text}
Total projected points with multipliers: {total_pts:.1f}

Provide your diagnostic breakdown addressing:
1. Operational Strengths (Tactical balance and explosive point vectors).
2. Vulnerability Index (The single weakest slot or risk exposure).
3. Strategic Optimization (One precise player swap with algorithmic justification).
4. Command Verification (Confirming or challenging the Captain/Vice-Captain selections).

Maintain a professional, highly analytical tone characteristic of an elite tactical advisor."""

    try:
        r = requests.post(OPENROUTER_URL, headers=HEADERS,
                          json={"model": MODEL, "messages":[{"role":"user","content":prompt}]},
                          timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ J.A.R.V.I.S. diagnostic review failed: {e}"

# ---------- CSV Export ----------
def lineup_to_csv(lineup):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Role", "Team", "Credits", "Points", "Ownership%", "Captain/VC"])
    for p, d in lineup:
        writer.writerow([p.name, p.role, p.team, p.salary, p.points,
                         p.ownership if p.ownership is not None else "",
                         "C" if d == "C" else ("VC" if d == "VC" else "")])
    csv_data = output.getvalue()
    b64 = base64.b64encode(csv_data.encode("utf-8")).decode("utf-8")
    return f"data:text/csv;base64,{b64}"

# ---------- Playing XI helpers ----------
def parse_playing_xi(text: str) -> List[str]:
    names = []
    for line in text.splitlines():
        parts = line.split(",")
        for part in parts:
            cleaned = part.strip()
            if not cleaned:
                continue
            if cleaned[0].isdigit():
                cleaned = cleaned.split(" ", 1)[-1] if " " in cleaned else cleaned
            names.append(cleaned)
    return names

def filter_by_playing_xi(players, xi_names):
    normalized_xi = {n.strip().lower() for n in xi_names}
    return [p for p in players if p.name.strip().lower() in normalized_xi]

def fetch_live_xi(match_id: str) -> Optional[List[str]]:
    if not CRICAPI_KEY or not match_id:
        return None
    try:
        url = "https://api.cricapi.com/v1/match_info"
        resp = requests.get(url, params={"apikey": CRICAPI_KEY, "id": match_id}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("data"):
            return None
        teams = data["data"].get("teams", {})
        xi = []
        for team in teams.values():
            for p in team.get("players", []):
                xi.append(p.get("name", ""))
        return [x for x in xi if x]
    except:
        return None

# ---------- Slate Storage ----------
SLATES = {}

def create_slate(name, players, deadline=None, match_id=None):
    sid = str(uuid.uuid4())
    SLATES[sid] = {
        "name": name,
        "players": players,
        "deadline": deadline,
        "match_id": match_id,
        "playing_xi": [],
        "xi_text": "",
        "current_team": "",
    }
    return sid

# ---------- Flask App ----------
app = Flask(__name__)

BASE_HTML_HEAD = """
<!doctype html>
<html>
<head><title>J.A.R.V.I.S. — DFS Control Center</title>
<style>
body { font-family: sans-serif; margin: 2em; background: #0f172a; color: #e2e8f0; }
.card { background: #1e293b; border-radius: 10px; padding: 1.5em; margin: 1em 0; box-shadow: 0 4px 6px rgba(0,0,0,0.3); border: 1px solid #334155; }
table { border-collapse: collapse; width: 100%; color: #e2e8f0; }
th, td { border: 1px solid #475569; padding: 8px; text-align: left; }
th { background: #334155; }
pre { white-space: pre-wrap; background: #0f172a; color: #38bdf8; padding: 1em; border-radius: 5px; border: 1px solid #334155; }
button, .btn { background: #0284c7; color: white; border: none; padding: 0.6em 1.2em; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; }
button:hover, .btn:hover { background: #0369a1; }
.btn-green { background: #16a34a; }
.btn-green:hover { background: #15803d; }
.btn-red { background: #dc2626; }
.warn { color: #facc15; background: #422006; border: 1px solid #854d0e; padding: 0.5em; border-radius: 5px; }
input, select, textarea { background: #0f172a; color: #f8fafc; border: 1px solid #475569; padding: 0.5em; border-radius: 4px; width: 100%; box-sizing: border-box; }
label { font-weight: bold; color: #94a3b8; display: block; margin-top: 0.8em; margin-bottom: 0.3em; }
</style>
</head>
<body>
"""

HOME_HTML = BASE_HTML_HEAD + """
<h1>🤖 J.A.R.V.I.S. Cricket DFS — Multi‑Slate Control Matrix</h1>
<div class="card">
    <h2>Initialize New Match Slate</h2>
    <form method="post" action="/create" enctype="multipart/form-data">
        <label>Slate Name:</label>
        <input type="text" name="slate_name" required>
        <label>Match City (for live weather protocols):</label>
        <input type="text" name="city" placeholder="e.g., Mumbai">
        <label>Match Deadline:</label>
        <input type="datetime-local" name="deadline">
        <label>Match ID (CricAPI Integration):</label>
        <input type="text" name="match_id" placeholder="e.g., 12345">
        <label>Upload Player Database (CSV):</label>
        <input type="file" name="file" accept=".csv" required><br><br>
        <button type="submit">Initialize Slate Protocols</button>
    </form>
</div>
<div class="card">
    <h2>Active Slates</h2>
    {% if slates %}
    <ul>
        {% for sid, slate in slates.items() %}
        <li style="margin: 0.5em 0;">
            <b>{{ slate.name }}</b> ({{ slate.players | length }} players)
            — <a href="{{ url_for('posttoss', slate_id=sid) }}" style="color: #38bdf8;">Access Terminal</a>
        </li>
        {% endfor %}
    </ul>
    {% else %}
    <p style="color: #94a3b8;">No active slates initialized.</p>
    {% endif %}
</div>
</body></html>
"""

POSTTOSS_PAGE = BASE_HTML_HEAD + """
<h1>🛡️ {{ slate.name }} — J.A.R.V.I.S. Post‑Toss Command Center</h1>
<a href="/" style="color: #38bdf8;">← Return to Control Matrix</a>

<div class="card">
    <h3>⏱️ Match Deadline Countdown</h3>
    <div id="countdown" style="font-size: 1.5em; font-weight: bold; color: #38bdf8;">--:--:--</div>
</div>

<div class="card">
    <h3>1. Environmental Conditions, Playing XI & Optimization Targets</h3>
    <form method="post" action="/posttoss">
        <input type="hidden" name="slate_id" value="{{ slate.id }}">

        <label>Platform Selector:</label>
        <select name="platform">
            <option value="dream11">Dream11</option>
            <option value="come11">Come11</option>
            <option value="both">Both</option>
        </select>

        <label>Weather Protocol:</label>
        <select name="weather">
            <option value="clear" {% if slate.weather == 'clear' %}selected{% endif %}>Clear</option>
            <option value="cloudy" {% if slate.weather == 'cloudy' %}selected{% endif %}>Cloudy</option>
            <option value="rain" {% if slate.weather == 'rain' %}selected{% endif %}>Rain</option>
            <option value="humid" {% if slate.weather == 'humid' %}selected{% endif %}>Humid</option>
        </select>
        <button type="button" onclick="fetchWeather()" class="btn" style="margin-top: 0.5em;">📡 Sync Live Weather</button>
        <span id="weather-status" style="margin-left: 1em; color: #38bdf8;"></span>

        <label>Pitch Dynamic:</label>
        <select name="pitch">
            <option value="neutral" {% if slate.pitch == 'neutral' %}selected{% endif %}>Neutral</option>
            <option value="flat" {% if slate.pitch == 'flat' %}selected{% endif %}>Flat</option>
            <option value="green" {% if slate.pitch == 'green' %}selected{% endif %}>Green</option>
            <option value="dusty" {% if slate.pitch == 'dusty' %}selected{% endif %}>Dusty</option>
        </select>

        <label>J.A.R.V.I.S. Rule — Minimum Base Player Score:</label>
        <input type="number" name="min_player_score" value="{{ slate.min_player_score or 50 }}" min="0" step="1">

        <label>J.A.R.V.I.S. Rule — Dream Team Score Target:</label>
        <input type="number" name="min_team_score" value="{{ slate.min_team_score or 1000 }}" min="0" step="1">

        <label>Official Playing XI (Paste Roster):</label>
        <textarea name="xi" placeholder="Virat Kohli&#10;Rohit Sharma&#10;Jos Buttler, Pat Cummins">{{ slate.xi_text }}</textarea><br><br>
        <button type="submit" class="btn-green">Execute Tactical Optimization</button>
    </form>
    <button onclick="fetchLiveXI()" class="btn" style="margin-top: 0.8em;">📡 Fetch Live Playing XI</button>
    <div id="live-status" style="margin-top: 0.5em; color: #38bdf8;"></div>
</div>

<div class="card">
    <h3>2. Squad Audit (Compare Your Current Roster)</h3>
    <form method="post" action="/posttoss">
        <input type="hidden" name="slate_id" value="{{ slate.id }}">
        <textarea name="current_team" placeholder="Paste your current 11 roster names">{{ slate.current_team }}</textarea><br><br>
        <button type="submit" class="btn">Audit Lineup Integrity</button>
    </form>
</div>

{% if not_playing %}
<div class="card warn">
    <b>⚠️ Tactical Warning — Missing from Official XI:</b> {{ not_playing | join(', ') }}
</div>
{% endif %}

{% if error %}
<div class="card" style="color:#f87171; background: #450a0a; border: 1px solid #991b1b;">
    {{ error }}
</div>
{% endif %}

{% if results %}
    {% for res in results %}
    <div class="card" style="border-color: #0284c7;">
        <h2>{{ res.platform }} — Optimized Post‑Toss XI</h2>
        <table>
            <tr><th>Player</th><th>Role</th><th>Team</th><th>Credits</th><th>Avg Pts</th><th>C/VC</th></tr>
            {% for p in res.lineup %}
            <tr>
                <td>{{ p.name }}</td><td>{{ p.role }}</td><td>{{ p.team }}</td>
                <td>{{ p.salary }}</td><td>{{ p.points }}</td>
                <td>{{ "C" if p.designation == "C" else ("VC" if p.designation == "VC" else "") }}</td>
            </tr>
            {% endfor %}
        </table>
        <p><b>Credits Consumed:</b> {{ res.credits_used }}/100 &nbsp;|&nbsp; <b>Projected Points:</b> {{ res.total_points }}</p>
        <a class="btn btn-green" href="{{ res.csv_link }}" download>⬇️ Export Roster CSV</a>
        <h3>🤖 J.A.R.V.I.S. Tactical Analysis</h3>
        <pre>{{ res.review }}</pre>
    </div>
    {% endfor %}
{% endif %}

{% if comparison %}
<div class="card">
    <h2>🧾 Roster Discrepancy Matrix (User vs Optimal)</h2>
    <table>
        <tr><th>Your Current Roster</th><th>Status</th><th>Optimized Tactical XI</th></tr>
        {% for row in comparison %}
        <tr><td>{{ row.your }}</td><td>{{ row.status }}</td><td>{{ row.opt }}</td></tr>
        {% endfor %}
    </table>
</div>
{% endif %}

<script>
const deadline = "{{ slate.deadline }}";
if (deadline) {
    const target = new Date(deadline).getTime();
    const timer = setInterval(() => {
        const now = new Date().getTime();
        const diff = target - now;
        if (diff <= 0) {
            document.getElementById('countdown').innerText = 'LOCKED — MATCH COMMENCED';
            clearInterval(timer);
        } else {
            const h = Math.floor(diff / (1000 * 60 * 60));
            const m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            const s = Math.floor((diff % (1000 * 60)) / 1000);
            document.getElementById('countdown').innerText = `${h}h ${m}m ${s}s`;
        }
    }, 1000);
}

function fetchLiveXI() {
    const slateId = "{{ slate.id }}";
    fetch(`/fetch_xi?slate_id=${slateId}`)
        .then(r => r.json())
        .then(data => {
            if (data.xi) {
                document.querySelector('textarea[name="xi"]').value = data.xi.join(', ');
                document.getElementById('live-status').innerText = '✅ Playing XI synchronized successfully.';
            } else {
                document.getElementById('live-status').innerText = '⚠️ API Key or Match ID missing. Manual entry required.';
            }
        });
}

function fetchWeather() {
    const slateId = "{{ slate.id }}";
    fetch(`/fetch_weather?slate_id=${slateId}`)
        .then(r => r.json())
        .then(data => {
            if (data.weather) {
                document.querySelector('select[name="weather"]').value = data.weather;
                document.getElementById('weather-status').innerText = `✅ Weather locked: ${data.weather}`;
            } else {
                document.getElementById('weather-status').innerText = '⚠️ Weather sync failed. Set manually.';
            }
        });
}
</script>
</body></html>
"""

@app.route("/")
def home():
    return render_template_string(HOME_HTML, slates=SLATES)

@app.route("/create", methods=["POST"])
def create():
    slate_name = request.form["slate_name"]
    city = request.form.get("city", "")
    deadline = request.form.get("deadline", "")
    match_id = request.form.get("match_id", "")
    file = request.files.get("file")
    if not file:
        return "No file provided", 400
    try:
        players = parse_csv(file.read().decode("utf-8-sig"))
    except Exception as e:
        return f"CSV parsing error: {e}", 400
    sid = create_slate(slate_name, players, deadline, match_id)
    SLATES[sid]["city"] = city
    SLATES[sid]["weather"] = "clear"
    SLATES[sid]["pitch"] = "neutral"
    SLATES[sid]["min_player_score"] = 50
    SLATES[sid]["min_team_score"] = 1000
    return redirect(url_for("posttoss", slate_id=sid))

@app.route("/posttoss")
def posttoss():
    slate_id = request.args.get("slate_id")
    if not slate_id or slate_id not in SLATES:
        return redirect("/")
    slate = SLATES[slate_id]
    return render_template_string(POSTTOSS_PAGE, slate=slate, results=None,
                                  comparison=None, not_playing=None, error=None)

@app.route("/fetch_xi")
def fetch_xi():
    slate_id = request.args.get("slate_id")
    if not slate_id or slate_id not in SLATES:
        return {"xi": None}
    slate = SLATES[slate_id]
    xi = fetch_live_xi(slate.get("match_id", ""))
    if xi:
        slate["playing_xi"] = xi
        slate["xi_text"] = ", ".join(xi)
    return {"xi": xi}

@app.route("/fetch_weather")
def fetch_weather():
    slate_id = request.args.get("slate_id")
    if not slate_id or slate_id not in SLATES:
        return {"weather": None}
    slate = SLATES[slate_id]
    weather = fetch_live_weather(slate.get("city", ""))
    if weather:
        slate["weather"] = weather
    return {"weather": weather}

@app.route("/posttoss", methods=["POST"])
def posttoss_post():
    slate_id = request.form["slate_id"]
    if slate_id not in SLATES:
        return redirect("/")
    slate = SLATES[slate_id]

    platform = request.form.get("platform", "dream11")
    weather = request.form.get("weather", "clear")
    pitch = request.form.get("pitch", "neutral")
    xi_text = request.form.get("xi", "")
    current_team_text = request.form.get("current_team", "")

    try:
        min_player_score = float(request.form.get("min_player_score", 50))
    except:
        min_player_score = 50
    try:
        min_team_score = float(request.form.get("min_team_score", 1000)) if request.form.get("min_team_score") else None
    except:
        min_team_score = None

    slate["weather"] = weather
    slate["pitch"] = pitch
    slate["min_player_score"] = min_player_score
    slate["min_team_score"] = min_team_score

    if xi_text.strip():
        slate["xi_text"] = xi_text
        slate["playing_xi"] = parse_playing_xi(xi_text)

    players = apply_conditions(slate["players"], weather, pitch)

    if slate["playing_xi"]:
        players = filter_by_playing_xi(players, slate["playing_xi"])

    if not players:
        return render_template_string(POSTTOSS_PAGE, slate=slate,
                                      error="Tactical Error: No players match the official playing XI after environmental adjustments.",
                                      results=None, comparison=None, not_playing=None)

    not_playing = []
    if current_team_text.strip():
        current_names = parse_playing_xi(current_team_text)
        slate["current_team"] = current_team_text
        normalized_xi = {n.strip().lower() for n in slate["playing_xi"]}
        not_playing = [n for n in current_names if n.strip().lower() not in normalized_xi]

    results = []
    plats = ["dream11", "come11"] if platform == "both" else [platform]
    for p in plats:
        cfg = PLATFORMS[p]
        lineup, total = optimize(players, cfg,
                                 min_player_score=min_player_score,
                                 min_team_score=min_team_score)
        if not lineup:
            results.append({"platform": cfg.name, "lineup": [],
                            "credits_used": 0, "total_points": 0,
                            "review": f"⚠️ Optimization constrained. No lineup meets the strict J.A.R.V.I.S. parameters (Base Player Score >= {min_player_score:.0f}, Dream Team Total >= {min_team_score:.0f}). Consider relaxing constraints.",
                            "csv_link": ""})
        else:
            formatted = [{"name": p.name, "role": p.role, "team": p.team,
                          "salary": p.salary, "points": p.points,
                          "ownership": p.ownership,
                          "designation": d} for p, d in lineup]
            credits = sum(x.salary for x, _ in lineup)
            total_disp = round(total, 2)
            review = gemini_review(lineup, total, cfg.name)
            csv_link = lineup_to_csv(lineup)
            results.append({"platform": cfg.name, "lineup": formatted,
                            "credits_used": credits, "total_points": total_disp,
                            "review": review, "csv_link": csv_link})

    comparison = None
    if current_team_text.strip():
        current_list = parse_playing_xi(current_team_text)
        opt_names = set()
        for p in lineup:
            opt_names.add(p[0].name.strip().lower())
        comp = []
        max_len = max(len(current_list), len(lineup))
        for i in range(max_len):
            your = current_list[i] if i < len(current_list) else ""
            opt = lineup[i][0].name if i < len(lineup) else ""
            status = ""
            if your:
                status = "✅ Keep" if your.strip().lower() in opt_names else "❌ Out"
            elif opt:
                status = "🔄 In"
            comp.append({"your": your, "opt": opt, "status": status})
        comparison = comp

    return render_template_string(POSTTOSS_PAGE, slate=slate, results=results,
                                  comparison=comparison, not_playing=not_playing,
                                  error=None)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
