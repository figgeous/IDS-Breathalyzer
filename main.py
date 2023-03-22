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

    def minutes_since_start_time(self):
        time_diff = datetime.now() - self.start_time
        return round(time_diff.total_seconds() / 60)

    def minutes_until_drive_time(self):
        if self.drive_time:
            time_diff = self.drive_time - datetime.now()
            return round(time_diff.total_seconds() / 60)
        else:
            return


def get_drinker(dob: int):
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


def save_drinker(drinker: Drinker) -> dict:
    drive_time = drinker.drive_time.isoformat() if drinker.drive_time else None
    drinkers[drinker.dob] = {
        "mode": drinker.mode,
        "sex": drinker.sex,
        "weight": drinker.weight,
        "start_time": drinker.start_time.isoformat(),
        "max_bac": drinker.max_bac,
        "drive_time": drive_time,
    }
    with open("drinkers.json", "w") as outfile:
        json.dump(drinkers, outfile)
    return drinkers


drinker = get_drinker(dob="200301028")
print(drinker.mode)
print(drinker.start_time)
print(drinker.drive_time)
print(drinker.minutes_since_start_time())
print(drinker.minutes_until_drive_time())
