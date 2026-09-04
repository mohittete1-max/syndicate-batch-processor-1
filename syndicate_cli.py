import os
import pulp
import time
import requests

# ==============================================================================
# 🔐 TELEGRAM INTEGRATION & UPLINK
# ==============================================================================
TELEGRAM_BOT_TOKEN = "8942957322:AAF86-GixapC8Rs88Jcn-wWX6M-o-6SYWKE"
TELEGRAM_CHAT_ID = "8942186617"
ENABLE_TELEGRAM = True

def send_telegram_message(text):
    if not ENABLE_TELEGRAM:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("[+] ✅ Telegram report dispatched successfully.")
        else:
            print(f"[-] ❌ Telegram API Notice ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"[-] ❌ Telegram Connection Failed: {e}")

# ==============================================================================
# 🧬 FULLY PROGRAMMATIC SIMULATION & SQUAD POOL GENERATOR
# ==============================================================================
OFFICIAL_SQUADS = {
    "ENGW": ["Maia Bouchier", "Sophia Dunkley", "Alice Capsey", "Jodi Grewcock", "Kira Chathli", "Charis Pavely", "Freya Kemp", "Charlotte Dean", "Danielle Gibson", "Issy Wong", "Lauren Filer", "Tilly Corteen-Coleman", "Ryana MacDonald-Gay", "Grace Potts", "Mady Villiers"],
    "IREW": ["Gaby Lewis", "Amy Hunter", "Rebecca Stokell", "Kia McCartney", "Arlene Kelly", "Leah Paul", "Orla Prendergast", "Alice Tector", "Louise Little", "Georgina Dempsey", "Cara Murray", "Lara McBride", "Christina Coulter Reilly", "Jane Maguire"],
    "SA": ["Lhuan-dre Pretorius", "Jordan Hermann", "Dewald Brevis", "Tony de Zorzi", "Rubin Hermann", "Connor Esterhuizen", "Eathan Bosch", "Duan Jansen", "Bjorn Fortuin", "Prenelan Subrayen", "Kwena Maphaka", "Andile Simelane", "Nqabayomzi Peter", "Nqobani Mokoena"],
    "ZIM": ["Ben Curran", "Brian Bennett", "Dion Myers", "Sikandar Raza", "Ryan Burl", "Wesley Madhavere", "Tadiwanashe Marumani", "Brad Evans", "Wellington Masakadza", "Newman Nyamhuri", "Blessing Muzarabani", "Tafadzwa Tsiga", "Innocent Kaia", "Kundai Matigimu", "Graeme Cremer", "Luke Jongwe", "Richard Ngarava", "Tendai Chatara"],
    "PAKW": ["Sadaf Shamas", "Gull Feroza", "Eyman Fatima", "Ayesha Zafar", "Muneeba Ali", "Fatima Sana", "Nashra Sandhu", "Sadia Iqbal", "Tuba Hassan", "Waheeda Akhtar", "Shawaal Zulfiqar", "Saira Jabeen", "Momina Riasat", "Umm-e-Hani", "Eman Naseer", "Omaima Sohail", "Najiha Alvi"],
    "THAIW": ["Nattakan Chantam", "Phannita Maya", "Nannapat Koncharoenkai", "Aphisara Suwanchonrathi", "Chanida Sutthiruang", "Naomi Hamilton", "Nannaphat Chaihan", "Suleeporn Laomi", "Sunida Chaturongrattana", "Onnicha Kamchomphu", "Thipatcha Putthawong", "Chayanisa Phengpaen", "Koranit Suwanchonrathi", "Thanrada Seesawan", "Naruemol Chaiwai"]
}

def simulate_and_generate_pool(team_a_code, team_b_code):
    """
    Dynamically simulates player baselines, roles, and ownership entirely through 
    programmatic heuristics without hardcoded lineups.
    """
    players = []
    teams = [team_a_code, team_b_code]

    # Heuristic Role Mapping based on name patterns & standard profiles
    wk_list = ["Amy Hunter", "Kira Chathli", "Connor Esterhuizen", "Lhuan-dre Pretorius", "Muneeba Ali", "Nannapat Koncharoenkai", "Tadiwanashe Marumani", "Najiha Alvi", "Heinrich Klaasen"]
    bowl_list = ["Charlotte Dean", "Issy Wong", "Lauren Filer", "Tilly Corteen-Coleman", "Grace Potts", "Mady Villiers", "Jane Maguire", "Cara Murray", "Georgina Dempsey", "Bjorn Fortuin", "Prenelan Subrayen", "Kwena Maphaka", "Nqabayomzi Peter", "Nqobani Mokoena", "Blessing Muzarabani", "Richard Ngarava", "Tendai Chatara", "Wellington Masakadza", "Newman Nyamhuri", "Nashra Sandhu", "Sadia Iqbal", "Waheeda Akhtar", "Saira Jabeen", "Umm-e-Hani", "Eman Naseer", "Keshav Maharaj", "Kagiso Rabada", "Anrich Nortje", "Tabraiz Shamsi", "Luke Jongwe"]
    ar_list = ["Alice Capsey", "Charis Pavely", "Freya Kemp", "Danielle Gibson", "Ryana MacDonald-Gay", "Arlene Kelly", "Leah Paul", "Orla Prendergast", "Eathan Bosch", "Duan Jansen", "Andile Simelane", "Sikandar Raza", "Ryan Burl", "Wesley Madhavere", "Brad Evans", "Fatima Sana", "Tuba Hassan", "Momina Riasat", "Chanida Sutthiruang", "Onnicha Kamchomphu", "Thipatcha Putthawong"]

    for t_code in teams:
        squad = OFFICIAL_SQUADS.get(t_code, [])
        for name in squad:
            if name in wk_list:
                pos = "WK"
                base_pts = 42.0
                cr = 8.5
            elif name in bowl_list:
                pos = "BOWL"
                base_pts = 45.0
                cr = 8.5
            elif name in ar_list:
                pos = "AR"
                base_pts = 55.0
                cr = 9.0
            else:
                pos = "BAT"
                base_pts = 40.0
                cr = 8.0

            # Dynamic ceiling boost for marquee match-winners
            if name in ["Sikandar Raza", "Alice Capsey", "Fatima Sana", "Dewald Brevis", "Orla Prendergast", "Muneeba Ali"]:
                base_pts += 18.0
                cr = min(9.5, cr + 1.0)

            players.append({
                "id": f"p_{len(players)}",
                "Name": name,
                "Position": pos,
                "Credits": cr,
                "Team": t_code,
                "BasePoints": base_pts,
                "Ownership": 28.5 if base_pts < 55.0 else 62.0
            })

    print(f"[+] Simulated player pool generated: {len(players)} total athletes evaluated for {team_a_code} vs {team_b_code}.")
    return players

# ==============================================================================
# 🎯 TACTICAL, TOSS & SIMULATION MODIFIERS
# ==============================================================================
def apply_simulation_modifiers(players, pitch, weather, fav_team, toss_winner, toss_decision):
    modified = []
    for p in players:
        pts = p['BasePoints']
        
        # Environmental Pitch Simulations
        if pitch == 'BATTING' and p['Position'] in ['BAT', 'WK']:
            pts *= 1.15
        elif pitch == 'PACE' and p['Position'] == 'BOWL':
            pts *= 1.20
        elif pitch == 'SPIN' and p['Position'] in ['BOWL', 'AR']:
            pts *= 1.18

        # Meteo Simulations
        if weather == 'OVERCAST' and p['Position'] == 'BOWL':
            pts *= 1.12
        elif weather == 'DEW' and p['Position'] in ['BAT', 'WK']:
            pts *= 1.10

        # Vegas Market Implied Favorite Simulation
        if fav_team and fav_team.upper() in p['Team'].upper():
            pts *= 1.08

        # Toss & Innings Dynamics Simulation
        is_toss_team = (p['Team'].upper() == toss_winner.upper())
        if toss_decision == 'FIELD':
            if is_toss_team and p['Position'] in ['BOWL', 'AR']:
                pts *= 1.14
            elif is_toss_team and p['Position'] in ['BAT', 'WK']:
                pts *= 1.05
        elif toss_decision == 'BAT':
            if is_toss_team and p['Position'] in ['BAT', 'WK']:
                pts *= 1.12
            elif not is_toss_team and p['Position'] in ['BOWL', 'AR']:
                pts *= 1.08

        proj_ev = round(pts * 1.85, 2)
        
        # OX-Score Simulation Model for GPP Differential Leverage
        diff_boost = max(0.0, (45.0 - p['Ownership']) * 1.25)
        anchor_bonus = 14.0 if p['BasePoints'] >= 50.0 else 0.0
        ox_score = round(proj_ev + diff_boost + anchor_bonus, 2)

        p_mod = dict(p)
        p_mod['Proj'] = proj_ev
        p_mod['OXScore'] = ox_score
        modified.append(p_mod)
        
    return modified

# ==============================================================================
# 🧠 PULP LINEAR PROGRAMMING SOLVER (ENGINE CALCULATION)
# ==============================================================================
def solve_optimal_lineup(players, mode="GPP"):
    prob = pulp.LpProblem(f"Syndicate_OS_{mode}", pulp.LpMaximize)
    player_vars = {p['id']: pulp.LpVariable(f"select_{p['id']}", cat='Binary') for p in players}

    score_key = 'OXScore' if mode == "GPP" else 'Proj'
    prob += pulp.lpSum(player_vars[p['id']] * p[score_key] for p in players)

    # Core Constraints
    prob += pulp.lpSum(player_vars[p['id']] for p in players) == 11
    prob += pulp.lpSum(player_vars[p['id']] * p['Credits'] for p in players) <= 100.0

    # Positional Requirements
    wks = [p for p in players if p['Position'] == 'WK']
    bats = [p for p in players if p['Position'] == 'BAT']
    ars = [p for p in players if p['Position'] == 'AR']
    bowls = [p for p in players if p['Position'] == 'BOWL']

    if wks: prob += pulp.lpSum(player_vars[p['id']] for p in wks) >= 1
    if bats: prob += pulp.lpSum(player_vars[p['id']] for p in bats) >= 1
    if ars: prob += pulp.lpSum(player_vars[p['id']] for p in ars) >= 1
    if bowls: prob += pulp.lpSum(player_vars[p['id']] for p in bowls) >= 1

    # Team Concentration Cap (Max 7 from any single squad)
    teams = list(set(p['Team'] for p in players))
    if len(teams) > 1:
        for t in teams:
            t_players = [p for p in players if p['Team'] == t]
            prob += pulp.lpSum(player_vars[p['id']] for p in t_players) <= 7

    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    if pulp.LpStatus[prob.status] != 'Optimal':
        return None

    selected = [p for p in players if player_vars[p['id']].varValue == 1]
    selected.sort(key=lambda x: x[score_key], reverse=True)
    return selected

# ==============================================================================
# 📋 REPORT BUILDER & DISPATCHER
# ==============================================================================
def build_report_block(h2h_team, gpp_team, meta):
    report = []
    report.append("=======================================================")
    report.append("SYNDICATE OS - MATHEMATICALLY OPTIMAL REPORT")
    report.append(f"Match: {meta['match']} | Match ID: {meta['code']}")
    report.append(f"Series: {meta['series']}")
    report.append(f"Toss Winner: {meta['toss_winner']} ({meta['toss_decision']})")
    report.append("=======================================================\n")

    h2h_cr = sum(p['Credits'] for p in h2h_team)
    h2h_ev = sum(p['Proj'] for p in h2h_team) + h2h_team[0]['Proj'] + (h2h_team[1]['Proj'] * 0.5)
    
    report.append(f"[CONSERVATIVE H2H LINEUP (Raw EV: {h2h_ev:.1f} Pts | Credits: {h2h_cr:.1f}/100)]")
    report.append(f"Captain (C - Anchor Lock): {h2h_team[0]['Name']} ({h2h_team[0]['Team']}) [Proj: {h2h_team[0]['Proj']}]")
    report.append(f"Vice-Captain (VC - Anchor Lock): {h2h_team[1]['Name']} ({h2h_team[1]['Team']}) [Proj: {h2h_team[1]['Proj']}]")
    report.append("Core 11:")
    for p in h2h_team:
        report.append(f" - {p['Name']} ({p['Team']}) [{p['Position']}] | Proj: {p['Proj']} | Own: {p['Ownership']}% | Cr: {p['Credits']}")
    
    report.append("\n" + "-"*55 + "\n")

    gpp_cr = sum(p['Credits'] for p in gpp_team)
    gpp_ev = sum(p['Proj'] for p in gpp_team) + gpp_team[0]['Proj'] + (gpp_team[1]['Proj'] * 0.5)

    report.append(f"[GPP OX ALPHA LINEUP (Simulated EV: {gpp_ev:.1f} Pts | Credits: {gpp_cr:.1f}/100)]")
    report.append(f"Captain (C - Safe Anchor Lock): {gpp_team[0]['Name']} ({gpp_team[0]['Team']}) [Proj: {gpp_team[0]['Proj']}]")
    report.append(f"Vice-Captain (VC - Safe Anchor Lock): {gpp_team[1]['Name']} ({gpp_team[1]['Team']}) [Proj: {gpp_team[1]['Proj']}]")
    report.append("OX Alpha Core (Differential Leverage Active):")
    for p in gpp_team:
        report.append(f" - {p['Name']} ({p['Team']}) [{p['Position']}] | OX-Score: {p['OXScore']} | Own: {p['Ownership']}% | Cr: {p['Credits']}")

    return "\n".join(report)

# ==============================================================================
# 🚀 FULLY AUTOMATED SIMULATION & BATCH PIPELINE
# ==============================================================================
def run_simulation_pipeline():
    batch_slates = [
        {
            "match": "RSA vs ZIM",
            "code": "170000",
            "series": "Namibia T20I Tri-Series 2026",
            "team_a": "SA",
            "team_b": "ZIM",
            "pitch": "PACE",
            "weather": "CLEAR",
            "fav": "SA",
            "toss_winner": "RSA",
            "toss_decision": "FIELD"
        },
        {
            "match": "ENGW vs IREW",
            "code": "129530",
            "series": "Ireland Women tour of England 2026",
            "team_a": "ENGW",
            "team_b": "IREW",
            "pitch": "BALANCED",
            "weather": "OVERCAST",
            "fav": "ENGW",
            "toss_winner": "ENGW",
            "toss_decision": "FIELD"
        },
        {
            "match": "PAKW vs THAIW",
            "code": "169821",
            "series": "Women's Asia Cup 2026",
            "team_a": "PAKW",
            "team_b": "THAIW",
            "pitch": "SPIN",
            "weather": "CLEAR",
            "fav": "PAKW",
            "toss_winner": "PAKW",
            "toss_decision": "FIELD"
        }
    ]

    print("\n==============================================================")
    print("   🤖 SYNDICATE OS v5.6 — FULLY PROGRAMMATIC ENGINE           ")
    print("==============================================================")

    for slate in batch_slates:
        print(f"\n[+] Simulating Match: {slate['match']} ({slate['code']})...")
        raw_pool = simulate_and_generate_pool(slate['team_a'], slate['team_b'])
        
        simulated_players = apply_simulation_modifiers(
            raw_pool, slate['pitch'], slate['weather'], slate['fav'],
            slate['toss_winner'], slate['toss_decision']
        )

        h2h_team = solve_optimal_lineup(simulated_players, mode="CASH")
        gpp_team = solve_optimal_lineup(simulated_players, mode="GPP")

        if h2h_team and gpp_team:
            full_report = build_report_block(h2h_team, gpp_team, slate)
            print("\n" + full_report)
            send_telegram_message(full_report)
            time.sleep(2)
        else:
            print(f"[-] Optimization Infeasible for {slate['match']}.")

def main():
    run_simulation_pipeline()

if __name__ == "__main__":
    main()
