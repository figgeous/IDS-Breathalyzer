import json
from dataclasses import dataclass
from datetime import datetime

from globals import *


@dataclass
class Drinker:
    username: str
    dob: int
    mode: int
    sex: str
    weight: int
    start_time: datetime
    max_bac: float
    drive_time: datetime

    def minutes_since_start_time(self) -> int:
        time_diff = datetime.now() - self.start_time
        return round(time_diff.total_seconds() / 60)

    def minutes_until_drive_time(self) -> int:
        if self.drive_time:
            time_diff = self.drive_time - datetime.now()
            return round(time_diff.total_seconds() / 60)
        else:
            return

    def save_to_db(self):
        drive_time = self.drive_time.isoformat() if self.drive_time else None
        drinkers[self.dob] = {
            "username": self.username,
            "mode": self.mode,
            "sex": self.sex,
            "weight": self.weight,
            "start_time": self.start_time.isoformat(),
            "max_bac": self.max_bac,
            "drive_time": self.drive_time.isoformat() if self.drive_time else None,
        }
        try:
            with open("databases/users.json", "w") as outfile:
                json.dump(drinkers, outfile)
        except Exception:
            print("Unable to load database file")
        return drinkers
