import pandas as pd
import plotly.express as px

class PostMatchCricketAnalyzer:
    def __init__(self, match_name):
        self.match_name = match_name
        
        # Pre-match Vegas implied shift vs Actual Dream Team Points
        self.matchdata = {
            "Shoaib Md Khan": {"team": "SMP", "shift": 0.0, "actual_pts": 420, "in_dream_team": True, "role": "AR"},
            "Atheeq Ur Rahman": {"team": "SMP", "shift": -0.6, "actual_pts": 207, "in_dream_team": True, "role": "AR"},
            "Emmanuel Cherian": {"team": "NRK", "shift": 9.8, "actual_pts": 132, "in_dream_team": True, "role": "BOWL"},
            "Ajitesh Guruswamy": {"team": "NRK", "shift": 6.3, "actual_pts": 90, "in_dream_team": True, "role": "WK"},
            "Gurjapneet Singh": {"team": "SMP", "shift": 3.1, "actual_pts": 89, "in_dream_team": True, "role": "BOWL"},
            "P Vignesh": {"team": "SMP", "shift": 2.2, "actual_pts": 87, "in_dream_team": True, "role": "BOWL"},
            "G Periyaswamy": {"team": "SMP", "shift": 2.5, "actual_pts": 76, "in_dream_team": True, "role": "BOWL"},
            "Hari Ragavendra V": {"team": "SMP", "shift": -0.7, "actual_pts": 71, "in_dream_team": True, "role": "BAT"},
            "Siddharth Mahadevan": {"team": "SMP", "shift": -0.8, "actual_pts": 45, "in_dream_team": True, "role": "BAT"},
            "Sachin Rathi": {"team": "NRK", "shift": 10.6, "actual_pts": 44, "in_dream_team": True, "role": "BOWL"},
            "Athish SR": {"team": "NRK", "shift": 0.0, "actual_pts": 29, "in_dream_team": True, "role": "BAT"},
            "Sonu Yadav": {"team": "NRK", "shift": 15.5, "actual_pts": 15, "in_dream_team": False, "role": "AR"},
            "Valliappan Yudheeswaran": {"team": "NRK", "shift": 11.6, "actual_pts": 20, "in_dream_team": False, "role": "BOWL"}
        }

    def generate_post_match_chart(self):
        """Generates a Plotly comparison chart of Vegas Shift vs Actual Dream Team Output."""
        df = pd.DataFrame([
            {
                "Player": p, 
                "Actual Fantasy Pts": d["actual_pts"], 
                "Team": d["team"],
                "In Dream Team": "Yes" if d["in_dream_team"] else "No"
            }
            for p, d in self.matchdata.items()
        ])
        df = df.sort_values(by="Actual Fantasy Pts", ascending=False)

        fig = px.bar(
            df,
            x="Player",
            y="Actual Fantasy Pts",
            color="In Dream Team",
            title=f"Post-Match Dream Team Analysis - {self.match_name}",
            color_discrete_map={"Yes": "#00e676", "No": "#ff5252"}
        )
        fig.update_layout(
            plot_bgcolor="#111111",
            paper_bgcolor="#111111",
            font_color="white",
            xaxis_tickangle=-45
        )
        print("[INFO] Rendering Post-Match Plotly comparison chart...")
        fig.show()

    def summarize_performance(self):
        print("\n" + "="*60)
        print(f"POST-MATCH MODEL AUDIT: {self.match_name}")
        print("="*60)
        dt_players = [p for p, d in self.matchdata.items() if d["in_dream_team"]]
        print(f"Total Dream Team Players Identified in Model Pool: {len(dt_players)}/11")
        print(f"Key Takeaway: Low-implied probability outliers (Shoaib Md Khan & Atheeq Ur Rahman)")
        print(f"secured the highest match points, proving that deep tournament volatility")
        print(f"can override pre-match bookmaker favoritism.")
        print("="*60)

if __name__ == "__main__":
    analyzer = PostMatchCricketAnalyzer("NRK vs SMP (TNPL Match 28)")
    analyzer.summarize_performance()
    analyzer.generate_post_match_chart()
