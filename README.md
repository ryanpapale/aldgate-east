# Aldgate East App
This application pulls data from the TFL API, 
stores it in a SQLite database, and visualizes 
it through a dashboard.

## Description
Data pulled includes arrivals, disruptions,
and crowding. This is a random project but 
it brings back many fond memories. I spent
so many years going in and out of this station.

## Structure
```
├── data
│   └── tfl.db
├── pyproject.toml
├── README.md
├── src
│   ├── app
│   │   └── main.py
│   └── tfl
│       ├── __init__.py
│       ├── database_client.py
│       ├── main.py
│       └── tfl_client.py
└── uv.lock
```

## Setup
Ensure that TFL API keys are set in the .env 
file and named PRIMARY_KEY and SECONDARY_KEY.