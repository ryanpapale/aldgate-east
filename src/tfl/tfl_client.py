import logging
import os
import requests
from tenacity import before_sleep_log, retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from datetime import datetime, timezone
from dotenv import load_dotenv
from requests.exceptions import RequestException
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

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

    @retry(
        retry=retry_if_exception_type(RequestException),
        stop = stop_after_attempt(3),
        wait = wait_fixed(2),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def pull_crowding(self) -> dict:
        r = self.SESSION.get(
            self.CROWDING_URL,
            params = self.PARAMS,
            timeout = 10
        )

        r.raise_for_status()

        js = r.json()

        if not isinstance(js, dict):
            raise ValueError("TfL crowding response not type dict")

        REQUIRED_KEYS = {"dataAvailable", "percentageOfBaseline", "timeUtc", "timeLocal"}
        missing_keys = REQUIRED_KEYS - js.keys()

        if missing_keys:
            raise ValueError("Tfl crowding returned missing keys")

        return js

    @retry(
        retry=retry_if_exception_type(RequestException),
        stop = stop_after_attempt(3),
        wait = wait_fixed(2),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def pull_disruptions(self) -> list[dict | None]:
        r = self.SESSION.get(
            self.DISRUPTIONS_URL,
            params = self.PARAMS,
            timeout = 10
        )

        r.raise_for_status()

        js = r.json()

        if not isinstance(js, list):
            raise ValueError("TfL disruptions response not type list")

        REQUIRED_KEYS = {"description"}
    
        disruptions = []
        lines = []
        for l in js:
            missing_keys = REQUIRED_KEYS - l.keys()

            if missing_keys:
                raise ValueError("Tfl disruptions returned missing keys")

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
                    "description": "Good service.",
                    "time_utc": str(datetime.now(timezone.utc)),
                    "time_local": str(datetime.now(ZoneInfo("Europe/London")))
                })

        return disruptions
        
    @retry(
        retry=retry_if_exception_type(RequestException),
        stop = stop_after_attempt(3),
        wait = wait_fixed(2),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def pull_arrivals(self) -> list[dict | None]:
        r = self.SESSION.get(
            self.ARRIVAL_URL,
            params = self.PARAMS,
            timeout = 10    
        )

        r.raise_for_status()

        js = r.json()

        if not isinstance(js, list):
            raise ValueError("TfL arrivals response not type list")

        REQUIRED_KEYS = {"lineName", "platformName", "destinationName", "expectedArrival", "timestamp"}

        arrivals = []
        for t in js:
            missing_keys = REQUIRED_KEYS - t.keys()

            if missing_keys:
                raise ValueError("Tfl arrivals returned missing keys")
            
            arrivals.append({
                "line": t["lineName"] + " Line",
                "platform": t["platformName"],
                "destination": t["destinationName"],
                "expected_arrival": t["expectedArrival"],
                "time_utc": t["timestamp"]
            })
                        
        return arrivals