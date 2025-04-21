# WMATA Station Board

A live, animated, Solari-style train board for any Washington Metro station, powered by the WMATA API.

Built with:
- Flask (Python)
- HTML/CSS/JavaScript
- Real-time WMATA API predictions

---

## Features

- Real-time train arrival updates every 30 seconds
- Flip-style animation when times change
- "ARR" blink effect for arriving trains
- Platform-aware layout (Upper / Lower)
- Two-column display grouped by line + destination
- One easy `config.txt` file for setup

---

## Project Structure

```
wmata-station-board/
├── app.py                     # Flask backend + WMATA API
├── config.txt                 # Your API key + default station
├── Station_List.xlsx          # Mapping of stations, lines, platforms
├── backup_station.xlsx        # Patching fallback for missing data, looking at you Brookland-CAU
├── templates/
│   └── index.html             # Frontend UI with flip logic
├── static/
│   └── style.css              # Board styling and animation
└── README.md                  # This file
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/wmata-station-board.git
cd wmata-station-board
```

### 2. Install Requirements

```bash
pip install flask pandas requests openpyxl
```

Works with Python 3.7–3.11

### 3. Get a WMATA API Key

- Sign up: https://developer.wmata.com/
- Create an app and copy the API key

### 4. Configure Your Station + API Key

Edit the `config.txt` file:

```txt
API_KEY=your_wmata_api_key_here
DEFAULT_STATION=Metro Center
```

You can choose any station listed in `Station_List.xlsx`

### 5. Run the App

```bash
python app.py
```

Then visit: http://localhost:5000.

---

## Raspberry Pi Display Tips

- Connect to monitor/TV
- Use `chromium-browser` in kiosk mode:
  ```bash
  chromium-browser --kiosk http://localhost:5000
  ```

- Use `cron` or a `systemd` service to run `app.py` at boot

---

## Station + Platform Mapping

The `Station_List.xlsx` includes:
- `DestinationName`
- `DestinationCode`
- `StationCode`
- Optional `Line` and `Platform` (Upper / Lower)

The `backup_station.xlsx` patches trains missing `Line` or `DestinationName`.

---


## License

MIT License
