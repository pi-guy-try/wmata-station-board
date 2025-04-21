from flask import Flask, render_template, request, jsonify
import pandas as pd
import requests
import os 
cwd = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

def load_config():
    config = {}
    with open(cwd+"/config.txt") as f:
        for line in f:
            if '=' in line:
                key, val = line.strip().split("=", 1)
                config[key.strip()] = val.strip()
    return config

config = load_config()
API_KEY = config.get("API_KEY")
DEFAULT_STATION = config.get("DEFAULT_STATION", "Wiehle-Reston East")

# Load station layout and fallback patching data
station_df = pd.read_csv(cwd+"/Station_List.csv")
backup_df = pd.read_csv(cwd+"/backup_station.csv")

# Build list of stations for dropdown menu
station_names = station_df["DestinationName"].dropna().drop_duplicates().sort_values().tolist()

@app.route("/")
def index():
    return render_template("index.html", stations=station_names, default_station=DEFAULT_STATION)

@app.route("/get_predictions")
def get_predictions():
    selected_station = request.args.get("station")
    if not selected_station:
        return jsonify({})

    platform_lookup = {
        str(row["StationCode"]).strip().upper(): str(row["Platform"]).strip()
        for _, row in station_df.iterrows()
        if pd.notna(row["StationCode"]) and pd.notna(row["Platform"])
    }

    platform_rows = station_df[
        (station_df["DestinationName"] == selected_station) &
        (station_df["Platform"].notna())
    ]
    use_platforms = not platform_rows.empty

    headers = {"api_key": API_KEY}
    url = "https://api.wmata.com/StationPrediction.svc/json/GetPrediction/All"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return jsonify({"error": "Failed to fetch WMATA data"}), 500

    all_trains = resp.json().get("Trains", [])

    filtered = [
        t for t in all_trains
        if t.get("LocationName") == selected_station and t.get("DestinationName") != "No Passenger"
    ]

    for train in filtered:
        line_missing = train.get("Line") in [None, "", "No", "--"]
        dest_missing = train.get("DestinationName") in [None, "", "Train", "--"]

        if line_missing or dest_missing:
            loc = str(train.get("LocationCode", "")).strip().upper()
            grp = str(train.get("Group", "")).strip()
            fallback = backup_df[
                (backup_df["LocationCode"].astype(str).str.strip().str.upper() == loc) &
                (backup_df["Group"].astype(str).str.strip() == grp)
            ]
            if not fallback.empty:
                if line_missing:
                    train["Line"] = fallback.iloc[0]["Line"]
                if dest_missing:
                    train["DestinationName"] = fallback.iloc[0]["DestinationName"]

    # Final grouped structure: line - group - label - trains
    grouped = {}

    if use_platforms:
        for train in filtered:
            location_code = str(train.get("LocationCode", "")).strip().upper()
            platform = platform_lookup.get(location_code)

            # If we still can't find a platform, skip it
            if not platform:
                continue

            line = train.get("Line", "UNK")
            group = str(train.get("Group", "0")).strip()
            label = f"{line} - {train['DestinationName']}"

            if platform not in grouped:
                grouped[platform] = {}
            if line not in grouped[platform]:
                grouped[platform][line] = {}
            if group not in grouped[platform][line]:
                grouped[platform][line][group] = {}
            grouped[platform][line][group].setdefault(label, []).append({
                "Line": line,
                "Car": train["Car"],
                "Destination": train["DestinationName"],
                "Min": train["Min"]
            })
    else:
        for train in filtered:
            line = train.get("Line", "UNK")
            group = str(train.get("Group", "0")).strip()
            label = f"{line} - {train['DestinationName']}"

            if line not in grouped:
                grouped[line] = {}
            if group not in grouped[line]:
                grouped[line][group] = {}
            grouped[line][group].setdefault(label, []).append({
                "Line": line,
                "Car": train["Car"],
                "Destination": train["DestinationName"],
                "Min": train["Min"]
            })

    return jsonify(grouped)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
