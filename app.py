from flask import Flask, render_template, request, redirect
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

# Define file paths
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")

TOWER_FILE = os.path.join(DATA_DIR, "tower1.xlsx")
STATUS_OPTIONS = ["TO DO", "IN PROGRESS", "BACKLOG", "COMPLETE"]

# Ensure log directory exists
os.makedirs(LOGS_DIR, exist_ok=True)

@app.route("/")
def index():
    try:
        df = pd.read_excel(TOWER_FILE, sheet_name="client list", engine="openpyxl")
        df["Client ID"] = df["Client ID"].astype(str)

        # Filter: only clients with Notifications = 1 and Coaching Client = 1
        filtered_df = df[(df["Notifications"] == 1) & (df["Coaching Client"] == 1)]
        client_ids = filtered_df["Client ID"].dropna().unique().tolist()

        return render_template("client_links.html", client_ids=client_ids)
    except Exception as e:
        return f"Error loading client list: {str(e)}", 500

@app.route("/client/<client_id>")
def client_view(client_id):
    try:
        df = pd.read_excel(TOWER_FILE, sheet_name="action items", engine="openpyxl")
        df["Client ID"] = df["Client ID"].astype(str)
        df = df[df["Client ID"] == str(client_id)]

        # Filter out completed items
        df = df[df["Status"].str.lower() != "COMPLETE"]

        if df.empty:
            return f"No pending action items found for client ID {client_id}.", 404

        items = df[["Action Items", "Status"]].reset_index(drop=True).to_dict(orient="index")
        return render_template(
            "client_view.html",
            client_id=client_id,
            items=items.items(),
            status_options=STATUS_OPTIONS
        )
    except Exception as e:
        return f"Error loading action items: {str(e)}", 500

@app.route("/submit", methods=["POST"])
def submit():
    client_id = request.form.get("client_id")
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    updates = []
    for key in request.form:
        if key.startswith("status_"):
            idx = key.split("_")[1]
            action_item = request.form.get(f"action_{idx}")
            status = request.form.get(key)
            if action_item:  # Skip blank actions
                updates.append({
                    "Client ID": client_id,
                    "Timestamp": timestamp,
                    "Action Item": action_item,
                    "Status": status
                })

    if not updates:
        return "No updates received.", 400

    try:
        log_df = pd.DataFrame(updates)
        log_file = os.path.join(LOGS_DIR, f"{client_id}_log.csv")

        if os.path.exists(log_file):
            log_df.to_csv(log_file, mode="a", header=False, index=False)
        else:
            log_df.to_csv(log_file, index=False)
    except Exception as e:
        return f"Error saving updates: {str(e)}", 500

    return redirect(f"/client/{client_id}")

# Bind to 0.0.0.0 and PORT env var for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
