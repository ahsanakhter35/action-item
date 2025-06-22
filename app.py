from flask import Flask, render_template, request, redirect
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

# Define relative paths
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")

TOWER_FILE = os.path.join(DATA_DIR, "tower1.xlsx")
STATUS_OPTIONS = ["To Do", "In Progress", "Backlog", "Complete"]

@app.route("/")
def index():
    try:
        df = pd.read_excel(TOWER_FILE, sheet_name="ClientList")
        client_ids = df["Client ID"].dropna().unique().tolist()
        return render_template("client_links.html", client_ids=client_ids)
    except Exception as e:
        return f"Error loading client list: {str(e)}", 500

@app.route("/client/<client_id>")
def client_view(client_id):
    try:
        df = pd.read_excel(TOWER_FILE, sheet_name="ActionItems")
        df = df[df["Client ID"] == client_id]
        items = df[["Action Item", "Status"]].reset_index(drop=True).to_dict(orient="index")
        return render_template("client_view.html", client_id=client_id, items=items.items(), status_options=STATUS_OPTIONS)
    except Exception as e:
        return f"Error loading action items: {str(e)}", 500

@app.route("/submit", methods=["POST"])
def submit():
    client_id = request.form.get("client_id")
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Collect updated statuses
    updates = []
    for key in request.form:
        if key.startswith("status_"):
            idx = key.split("_")[1]
            action_item = request.form.get(f"action_{idx}")
            status = request.form.get(key)
            updates.append({"Client ID": client_id, "Timestamp": timestamp, "Action Item": action_item, "Status": status})

    # Save to logs folder
    if updates:
        log_df = pd.DataFrame(updates)
        os.makedirs(LOGS_DIR, exist_ok=True)
        log_file = os.path.join(LOGS_DIR, f"{client_id}_log.csv")
        if os.path.exists(log_file):
            log_df.to_csv(log_file, mode="a", header=False, index=False)
        else:
            log_df.to_csv(log_file, index=False)

    return redirect(f"/client/{client_id}")

if __name__ == "__main__":
    app.run(debug=True)
