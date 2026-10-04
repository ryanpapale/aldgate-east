import os
import requests

from datetime import datetime, timezone
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

class tflClient:
    def __init__(self) -> None:
        self.SESSION = requests.Session()

        self.ALL_LINES = [
            "Hammersmith and City Line",
            "District Line"
        ]

        self.ALDGATE_EAST_NAPTAN = "940GZZLUADE"
        self.LINE_IDS = ["district", "hammersmith-city"]
        self.LINE_IDS_CSV =  ", ".join(self.LINE_IDS)

        self.CROWDING_URL = f"https://api.tfl.gov.uk/crowding/{self.ALDGATE_EAST_NAPTAN}/Live"
        self.DISRUPTIONS_URL = f"https://api.tfl.gov.uk/Line/{self.LINE_IDS_CSV}/Disruption"
        self.ARRIVAL_URL = f"https://api.tfl.gov.uk/Line/{self.LINE_IDS_CSV}/Arrivals/{self.ALDGATE_EAST_NAPTAN}"

        load_dotenv()
        self.PRIMARY_KEY = os.getenv("PRIMARY_KEY")
        self.SECONDARY_KEY = os.getenv("SECONDARY_KEY")

        if not self.PRIMARY_KEY and not self.SECONDARY_KEY:
            raise KeyError("Missing Primary and Secondary API keys")

        if not self.PRIMARY_KEY:
            self.PRIMARY_KEY = self.SECONDARY_KEY

        self.PARAMS = {
            "app_key": self.PRIMARY_KEY
        }

    def pull_crowding(self) -> dict:
        try:
            r = self.SESSION.get(self.CROWDING_URL, params = self.PARAMS)
            r.raise_for_status()

            return r.json()
        
        except:
            return {
                "dataAvailable": False,
                "percentageOfBaseline": None,
                "timeUtc": str(datetime.now(timezone.utc)),
                "timeLocal": str(datetime.now(ZoneInfo("Europe/London")))
            }

    def pull_disruptions(self) -> dict:
        try:
            r = self.SESSION.get(self.DISRUPTIONS_URL, params = self.PARAMS)

            js = r.json()
            disruptions = []
            lines = []

            for l in js:
                disruptions.append({
                    "line": l["description"].split(":")[0].strip(),
                    "description": l["description"].split(":")[1].strip(),
                    "time_utc": str(datetime.now(timezone.utc)),
                    "time_local": str(datetime.now(ZoneInfo("Europe/London")))
                })

                lines.append(l["description"].split(":")[0].strip())

            missing_lines = [l for l in self.ALL_LINES if l not in lines]
   
            if len(missing_lines) > 0:
                for l in missing_lines:
                    disruptions.append({
                        "line": l,
                        "description": "GOOD SERVICE.",
                        "time_utc": str(datetime.now(timezone.utc)),
                        "time_local": str(datetime.now(ZoneInfo("Europe/London")))
                    })

            return disruptions

        except:
            return [{
                "line": "",
                "description": "",
                "time_utc": str(datetime.now(timezone.utc)),
                "time_local": str(datetime.now(ZoneInfo("Europe/London")))
            }]
        

    def pull_arrivals(self) -> list:
        r = self.SESSION.get(self.ARRIVAL_URL, params = self.PARAMS)
        js = r.json()

        try:
            arrivals = []
            for t in js:
                arrivals.append({
                    "line": t["lineName"] + " Line",
                    "platform": t["platformName"],
                    "destination": t["destinationName"],
                    "expected_arrival": t["expectedArrival"],
                    "time_utc": t["timestamp"]
                })
                            
            return arrivals

        except:
            return {
                "line": "",
                "platform": "",
                "destination": "",
                "expected_arrival": "",
                "time_utc": str(datetime.now(timezone.utc))
            }

if __name__ == "__main__":
    tfl = tflClient()
    test = tfl.pull_arrivals()
