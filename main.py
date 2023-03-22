import json
from dataclasses import dataclass
from datetime import datetime

with open("drinkers.json", "r") as infile:
    drinkers = json.load(infile)


@dataclass
class Drinker:
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
            "mode": self.mode,
            "sex": self.sex,
            "weight": self.weight,
            "start_time": self.start_time.isoformat(),
            "max_bac": self.max_bac,
            "drive_time": self.drive_time.isoformat() if self.drive_time else None,
        }
        try:
            with open("drinkers.json", "w") as outfile:
                json.dump(drinkers, outfile)
        except Exception:
            print("Unable to load database file")
        return drinkers


def get_drinker(dob: int) -> Drinker:
    if dob not in drinkers:
        return

    d = drinkers[dob]
    start_time = datetime.fromisoformat(d["start_time"])
    drive_time = datetime.fromisoformat(d["drive_time"]) if d["drive_time"] else None
    drinker = Drinker(
        dob,
        d["mode"],
        d["sex"],
        d["weight"],
        start_time,
        d["max_bac"],
        drive_time,
    )
    return drinker


drinker = get_drinker(dob="20031028")
print(drinker.mode)
print(drinker.start_time)
print(drinker.drive_time)
print(drinker.minutes_since_start_time())
print(drinker.minutes_until_drive_time())

drinker.save_to_db()
