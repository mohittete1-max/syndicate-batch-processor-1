# app1.py
import os
import gradio as gr
import pandas as pd
import pulp
import requests

TELEGRAM_TOKEN = "8939525053:AAETS86KY5ojo9Tf3eC1SfKKGbqgVYPJA8A"
TELEGRAM_CHAT_ID = "1432527576"

def push_to_telegram(message_text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message_text, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram webhook failed: {e}")

def run_syndicate_app(venue, locks):
    # Match 1 Logic & Data placeholder
    html_output = f"<h3>Match 1 Portfolio Active ({venue})</h3><p>Locked: {locks}</p>"
    push_to_telegram(f"🚨 *MATCH 1 PORTFOLIO GENERATED*\nVenue: {venue}")
    return html_output, None

with gr.Blocks(title="Apex Alpha OS - Match 1") as demo:
    gr.Markdown("# 🏏 Apex Alpha OS: Match 1")
    v_drop = gr.Dropdown(choices=["Venue A", "Venue B"], value="Venue A", label="Match 1 Venue")
    l_box = gr.Textbox(value="", label="Core Locks")
    btn = gr.Button("Generate Match 1 Portfolio", variant="primary")
    out = gr.HTML()
    btn.click(fn=run_syndicate_app, inputs=[v_drop, l_box], outputs=[out])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, theme=gr.themes.Soft())
