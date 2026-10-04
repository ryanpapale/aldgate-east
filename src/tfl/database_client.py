from pathlib import Path
import polars as pl
import sqlite3

class database:
    def __init__(self) -> None:
        self.PATH_DATA = Path(Path(__file__).resolve().parent.parent.parent, "data")
        self.PATH_DATA.mkdir(parents = True, exist_ok = True)

    def init_db(self) -> None:
        # if not Path(self.PATH_DATA, "tfl.db").exists():
        with sqlite3.connect("data/tfl.db") as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS crowding (
                    id INTEGER PRIMARY KEY,
                    data_available BOOLEAN,
                    percentage_baseline REAL,
                    time_utc TEXT,
                    time_local TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS disruptions (
                    id INTEGER PRIMARY KEY,
                    line TEXT, 
                    description TEXT,
                    time_utc TEXT,
                    time_local TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS arrivals (
                    id INTEGER PRIMARY KEY,
                    line TEXT, 
                    platform TEXT,
                    destination TEXT,
                    expected_arrival TEXT,
                    time_utc TEXT
                )
            """)
    
    def write_crowding(self, js: dict) -> None:
            conn = sqlite3.connect(Path(self.PATH_DATA, "tfl.db"))
                
            curs = conn.cursor()
            curs.execute("""
                INSERT INTO crowding (data_available, percentage_baseline, time_utc, time_local)
                VALUES (?, ?, ?, ?)""",
                (js["dataAvailable"], js["percentageOfBaseline"], js["timeUtc"], js["timeLocal"])
            )

            conn.commit()
            conn.close()

    def write_disruptions(self, ls: list) -> None:
            conn = sqlite3.connect(Path(self.PATH_DATA, "tfl.db"))
                
            curs = conn.cursor()
            curs.executemany("""
                INSERT INTO disruptions (line, description, time_utc, time_local)
                VALUES (:line, :description, :time_utc, :time_local)""",
                ls
            )

            conn.commit()
            conn.close()

    def write_arrivals(self, ls: list) -> None:
            conn = sqlite3.connect(Path(self.PATH_DATA, "tfl.db"))
                
            curs = conn.cursor()
            curs.executemany("""
                INSERT INTO arrivals (line, platform, destination, expected_arrival, time_utc)
                VALUES (:line, :platform, :destination, :expected_arrival, :time_utc)""",
                ls
            )

            conn.commit()
            conn.close()

    def read_db(self) -> pl.dataframe:
        conn = sqlite3.connect(Path(self.PATH_DATA, "tfl.db"))
                
        df_crowding = pl.read_database("SELECT * FROM crowding", connection = conn)
        df_disruptions = pl.read_database("SELECT * FROM disruptions", connection = conn)
        df_arrivals = pl.read_database("SELECT * FROM arrivals", connection = conn)

        conn.close()

        return df_crowding, df_disruptions, df_arrivals

if __name__ == "__main__":
    db = database()
    db.read_db()