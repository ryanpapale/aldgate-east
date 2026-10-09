
import logging
import time

from logging.handlers import RotatingFileHandler
from tfl.database_client import database
from tfl.tfl_client import tflClient

logging.basicConfig(
    handlers=[RotatingFileHandler('./.log', maxBytes=100000, backupCount=2)],
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt='%Y-%m-%dT%H:%M:%S'
)

logger = logging.getLogger(__name__)

def pull_write(fn_read, fn_write) -> None:
    data = fn_read()
    fn_write(data)    

def main():
    logger.info("Starting Aldgate East App.")

    db = database()
    tfl = tflClient()

    while True:
        try:
            pull_write(tfl.pull_arrivals, db.write_arrivals)
        except:
            logger.exception("Skipping arrivals for this cycle.")

        try:
            pull_write(tfl.pull_crowding, db.write_crowding)
        except:
            logger.exception("Skipping crowding for this cycle.")

        try:
            pull_write(tfl.pull_disruptions, db.write_disruptions)
        except:
            logger.exception("Skipping disruptions for this cycle.")

        time.sleep(60)

if __name__ == "__main__":
    main()