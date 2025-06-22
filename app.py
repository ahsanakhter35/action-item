from flask import Flask, render_template, request, redirect
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

# Paths (update if deploying to cloud or using env variables)
DATA_PATH = "/Users/ahsanakhter/Library/Mobile Documents/com~apple~CloudDocs/tower leadership/codes/action-items/data/tower1.xlsx"
LOG_FOLDER = "/Users/ahsanakhter/Library/Mobile Documents/com~apple~CloudDocs/tower leadership/codes/action-items/logs"

@app.route('/')
def home():
    df = pd.read_excel(DATA_PATH, sheet_name=0)
    filtered = df[(df["Coaching Client"] == 1) & (df["Notifications"] == 1)]
    client_ids = filtered["Client ID"].dropna().unique().tolist()
    return render_template('client_links.html', client_ids=client_ids)

@app.route('/client/<client_id>', methods=['GET', 'POST'])
def client_view(client_id):
    df = pd.read_excel(DATA_PATH, sheet_name=0)
    client_df = df[df["Client ID"] == client_id]

    if request.method == 'POST':
        updates = []
        for item in client_df["Action Items"]:
            new_status = request.form.get(item)
            if new_status:
                updates.append({
                    "Client ID": client_id,
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Action Item": item,
                    "Status": new_status
                })

        if updates:
            log_df = pd.DataFrame(updates)
            os.makedirs(LOG_FOLDER, exist_ok=True)
            log_file = os.path.join(LOG_FOLDER, f"{client_id}_log.csv")

            if os.path.exists(log_file):
                existing_log = pd.read_csv(log_file)
                log_df = pd.concat([existing_log, log_df], ignore_index=True)

            log_df.to_csv(log_file, index=False)

        return redirect(f"/client/{client_id}")

    return render_template('client_view.html', client_id=client_id, client_data=client_df)

# This allows local running via `python app.py`
if __name__ == '__main__':
    app.run(debug=True)
