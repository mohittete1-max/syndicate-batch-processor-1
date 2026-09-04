# ledger.py - Apex Alpha OS: Bankroll Ledger & Profit Tracker
# Protocols: CSV Database Management, Automated ROI Calculation, Dual-Port Execution

import os
import gradio as gr
import pandas as pd

# Define the local database file path
DB_FILE = "bankroll_database.csv"

def initialize_db():
    """Creates the CSV database if it doesn't exist yet."""
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["Match_Name", "Date", "Total_Investment", "Total_Returns", "Net_Profit"])
        df.to_csv(DB_FILE, index=False)

def calculate_metrics(df):
    """Calculates overall financial metrics."""
    if df.empty:
        return "### 💰 Total Investment: Rs 0 | 📈 Total Returns: Rs 0 | 🏆 Net Profit: Rs 0 | 📊 ROI: 0.00%"
    
    total_inv = df["Total_Investment"].sum()
    total_ret = df["Total_Returns"].sum()
    total_profit = df["Net_Profit"].sum()
    roi = (total_profit / total_inv * 100) if total_inv > 0 else 0.0
    
    # Determine color based on profit
    profit_color = "#4CAF50" if total_profit >= 0 else "#ff5252"
    
    return f"""
    <div style='background: #1a1a1a; padding: 20px; border-radius: 8px; border-left: 5px solid {profit_color}; margin-bottom: 20px;'>
        <h3 style='margin: 0; color: #eee;'>💰 Total Investment: <span style='color: #fff;'>Rs {total_inv:,.2f}</span></h3>
        <h3 style='margin: 10px 0; color: #eee;'>📈 Total Returns: <span style='color: #03a9f4;'>Rs {total_ret:,.2f}</span></h3>
        <h2 style='margin: 0; color: {profit_color};'>🏆 Net Profit: Rs {total_profit:,.2f} (ROI: {roi:.2f}%)</h2>
    </div>
    """

def add_ledger_entry(match_name, match_date, investment, returns):
    """Adds a new match result to the database and updates the ledger."""
    try:
        initialize_db()
        df = pd.read_csv(DB_FILE)
        
        # Calculate individual match profit
        net_profit = returns - investment
        
        # Append new data
        new_entry = pd.DataFrame([{
            "Match_Name": match_name,
            "Date": match_date,
            "Total_Investment": investment,
            "Total_Returns": returns,
            "Net_Profit": net_profit
        }])
        
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(DB_FILE, index=False)
        
        # Return updated metrics and the updated table
        return calculate_metrics(df), df
    except Exception as e:
        return f"<div style='color: #ff5252;'>Error saving entry: {str(e)}</div>", pd.DataFrame()

def load_initial_data():
    """Loads data when the app starts."""
    initialize_db()
    df = pd.read_csv(DB_FILE)
    return calculate_metrics(df), df

# --- Gradio UI Layout ---
with gr.Blocks(title="Apex Alpha OS - Bankroll Ledger") as demo:
    gr.Markdown("# 🏦 Apex Alpha OS: Bankroll Ledger & Tracker")
    gr.Markdown("Permanent local database to track Grand League investments, returns, and total ROI.")
    
    with gr.Row():
        metrics_panel = gr.HTML()
        
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📝 Log New Match Result")
            match_input = gr.Textbox(label="Match Name (e.g., ENG vs PAK 1st Test)")
            date_input = gr.Textbox(label="Date (YYYY-MM-DD)")
            inv_input = gr.Number(label="Total Investment (Rs)", value=0)
            ret_input = gr.Number(label="Total Returns (Rs)", value=0)
            log_btn = gr.Button("💾 Save to Ledger", variant="primary")
            
        with gr.Column():
            gr.Markdown("### 📊 Historical Ledger")
            ledger_table = gr.Dataframe(interactive=False)

    # Load data on startup
    demo.load(fn=load_initial_data, outputs=[metrics_panel, ledger_table])
    
    # Trigger save action
    log_btn.click(
        fn=add_ledger_entry, 
        inputs=[match_input, date_input, inv_input, ret_input], 
        outputs=[metrics_panel, ledger_table]
    )

if __name__ == "__main__":
    # Running on Port 7861 so it doesn't conflict with app.py on Port 7860
    port = int(os.environ.get("PORT", 7861))
    demo.launch(server_name="0.0.0.0", server_port=port, theme=gr.themes.Soft())
