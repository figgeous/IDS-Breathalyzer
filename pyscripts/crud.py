import json
from dataclasses import dataclass
from datetime import datetime

with open("databases/users.json", "r") as infile:
    drinkers = json.load(infile)


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


def get_drinker(drinkers: dict, username: str) -> Drinker:
    d = drinkers[username]
    start_time = datetime.fromisoformat(d["start_time"])
    drive_time = datetime.fromisoformat(d["drive_time"]) if d["drive_time"] else None
    drinker = Drinker(
        username,
        d["dob"],
        d["mode"],
        d["sex"],
        d["weight"],
        start_time,
        d["max_bac"],
        drive_time,
    )
    return drinker


# drinker = get_drinker(drinkers, "user123")
# print(drinker)
# drinker.sex = "female"
# drinker.save_to_db()

# drinker2 = Drinker(
# username='user123',
# dob=1990,
# mode=1,
# sex="male",
# weight=150,
# start_time=datetime(2021, 3, 29, 20, 30, 10, 123456),
# max_bac=0.0,
# drive_time=datetime(2021, 3, 29, 20, 30, 10, 123456)
# )
# drinker2.save_to_db()
