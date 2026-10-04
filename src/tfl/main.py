import time

from tfl.database_client import database
from tfl.tfl_client import tflClient

def main():
    db = database()
    db.init_db()

    tfl = tflClient()

    while True:
        js_crowd = tfl.pull_crowding()
        ls_disruptions = tfl.pull_disruptions()
        ls_arrivals = tfl.pull_arrivals()

        # Crowding
        try:
            db.write_crowding(js_crowd)

        except:
            time.sleep(5)
            db.write_crowding(js_crowd)
        
        finally:
            pass
        
        # Disruptions
        try:
            db.write_disruptions(ls_disruptions)

        except:
            time.sleep(5)
            db.write_disruptions(ls_disruptions)
        
        finally:
            pass

        # Arrivals
        try:
            db.write_arrivals(ls_arrivals)

        except:
            time.sleep(5)
            db.write_arrivals(ls_arrivals)
        
        finally:
            pass

        time.sleep(300)

if __name__ == "__main__":
    main()