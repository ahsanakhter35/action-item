from flask import Flask, render_template, request, redirect
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

# Paths
BASE_DIR = "/Users/ahsanakhter/Library/Mobile Documents/com~apple~CloudDocs/tower leadership/codes/action-items"
TOWER_FILE = os.path.join(BASE_DIR, "data", "tower1.xlsx")
LOG_FOLDER = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_FOLDER, "action_log.csv")

@app.route("/")
def index():
    df = pd.read_excel(TOWER_FILE, sheet_name="ClientList")
    filtered = df[(df["Coaching Client"] == 1) & (df["Notifications"] == 1)]
    client_ids = filtered["Client ID"].dropna().unique().tolist()
    return render_template("client_links.html", client_ids=client_ids)

@app.route("/client/<client_id>")
def client_view(client_id):
    df = pd.read_excel(TOWER_FILE, sheet_name="ActionItems")
    client_data = df[(df["Client ID"] == client_id) & (df["Status"] != "Complete")].copy()
    items = list(client_data[["Action Item", "Status"]].to_dict(orient="records"))
    return render_template("client_view.html",
                           client_id=client_id,
                           items=enumerate(items),
                           status_options=["To Do", "In Progress", "Complete", "Backlog"])

@app.route("/submit", methods=["POST"])
def submit():
    client_id = request.form.get("client_id")
    df = pd.read_excel(TOWER_FILE, sheet_name="ActionItems")
    client_data = df[df["Client ID"] == client_id].copy()
    client_data = client_data[client_data["Status"] != "Complete"].copy()

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    log_entries = []

    for idx, (_, row) in enumerate(client_data.iterrows()):
        new_status = request.form.get(f"status_{idx}")
        if new_status and new_status != row["Status"]:
            log_entries.append({
                "Client ID": client_id,
                "Timestamp": now,
                "Action Item": row["Action Item"],
                "Status": new_status
            })

    if log_entries:
        log_df = pd.DataFrame(log_entries)
        if os.path.exists(LOG_FILE):
            log_df.to_csv(LOG_FILE, mode="a", header=False, index=False)
        else:
            os.makedirs(LOG_FOLDER, exist_ok=True)
            log_df.to_csv(LOG_FILE, index=False)

    return redirect(f"/client/{client_id}")

if __name__ == "__main__":
    app.run(debug=True)