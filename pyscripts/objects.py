import json
import os
from datetime import datetime


def get_drinkers() -> dict:
    try:
        with open("databases/users.json", "r") as infile:
            drinkers = json.load(infile)
    except Exception:
        print("Unable to load database file")
    return drinkers


class Drinker:
    username: str
    dob: int
    mode: int
    sex: str
    weight: int
    start_time: datetime
    max_bac: float
    drive_time: datetime

    def __init__(
        self, username, password, dob, mode, sex, weight, start_time, max_bac, drive_time
    ):
        self.username = username
        self.password = password
        self.dob = dob
        self.mode = mode
        self.sex = sex
        self.weight = weight
        self.start_time = start_time
        self.max_bac = max_bac
        self.drive_time = drive_time

    @staticmethod
    def get_from_db(username: str) -> "Drinker":
        drinkers = get_drinkers()

        if username not in drinkers:
            return None

        d = drinkers[username]
        start_time = datetime.fromisoformat(d["start_time"])
        drive_time = (
            datetime.fromisoformat(d["drive_time"]) if d["drive_time"] else None
        )
        drinker = Drinker(
            username=username,
            password=d["password"],
            dob=d["dob"],
            mode=d["mode"],
            sex=d["sex"],
            weight=d["weight"],
            start_time=start_time,
            max_bac=d["max_bac"],
            drive_time=drive_time,
        )
        return drinker

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
        drinkers = get_drinkers()
        drinkers[self.username] = {
            "username": self.username,
            "password": self.password,
            "dob": self.dob,
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
                print("Saved to database")
        except Exception:
            print("Unable to load database file")
        return drinkers

    def __str__(self):
        return f"Drinker: {self.username} - {self.dob} - {self.mode} - {self.start_time} - {self.max_bac} - {self.drive_time}"
