import dataclasses
import json
import logging
from datetime import datetime, timedelta


def get_drinkers() -> dict:
    try:
        with open("databases/users.json", "r") as infile:
            drinkers = json.load(infile)
    except Exception:
        print("Unable to load database file")
    return drinkers

def get_all_beverages_from_db():
    try:
        with open("databases/beverages.json", "r") as infile:
            beverages_from_db = json.load(infile)
    except Exception as e:
        print("Unable to load database file", e)

    beverages_list = []
    for _, beverage in beverages_from_db.items():
        beverages = Drink(
            name=beverage["name"],
            type=beverage["type"],
            alcohol_content=float(beverage["alcohol_content"]),
            ingredients=beverage["ingredients"],
            image_path=beverage["image_path"],
        )
        beverages_list.append(beverages)
    return beverages_list

def get_session_from_db(id: int) -> dict:
    sessions_from_db = get_all_sessions_from_db()
    return sessions_from_db.get(str(id), None)

def get_session_object_from_db(id:int) -> "Session":
    session_dict = get_session_from_db(id=id)
    return Session(
        id=id,
        username=session_dict["username"],
        mode=session_dict["mode"],
        max_alcohol=float(session_dict["max_alcohol"]),
        start_time=datetime.fromisoformat(session_dict["start_time"]),
        drive_time=datetime.fromisoformat(session_dict["drive_time"]),
    )
def get_all_sessions_from_db() -> dict[str,dict]:
    try:
        with open("databases/sessions.json", "r") as infile:
            sessions_from_db = json.load(infile)
    except Exception as e:
        logging.error("Unable to load database file", e)
    return sessions_from_db
def get_all_session_objects_from_db() -> list["Session"]:
    sessions_from_db = get_all_sessions_from_db()
    sessions = []
    for session_id, session_from_db in sessions_from_db.items():
        session = Session(
            id=int(session_id),
            username=session_from_db["username"],
            mode=int(session_from_db["mode"]),
            max_alcohol=float(session_from_db["max_alcohol"]),
            start_time=datetime.fromisoformat(session_from_db["start_time"]),
            drive_time=datetime.fromisoformat(session_from_db["drive_time"]),
        )
        sessions.append(session)
    return sessions

class Drinker:
    username: str
    dob: datetime
    mode: int
    sex: str
    weight: int
    session: int or None # Foreign key to current session

    def __init__(
        self, username, password, dob, sex, weight
    ):
        self.username = username
        self.password = password
        self.dob = dob
        self.sex = sex.lower()
        self.weight = weight

    @staticmethod
    def get_drinker_from_db(username: str) -> "Drinker":
        drinkers = get_drinkers()

        if username not in drinkers:
            return None

        d = drinkers[username]
        drinker = Drinker(
            username=username,
            password=d["password"],
            dob=d["dob"],
            sex=d["sex"],
            weight=int(d["weight"]),
        )
        return drinker

    def get_most_recent_session(self) -> "Session" or None:
        sessions_from_db = get_all_session_objects_from_db()
        # Get session for user with most recent start time
        most_recent_session = None
        for session in sessions_from_db:
            if session.username != self.username:
                continue
            if most_recent_session is None:
                most_recent_session = session
            elif session.start_time > most_recent_session.start_time:
                most_recent_session = session
        return most_recent_session

    def get_current_session(self) -> "Session" or None:
        """
        Returns the current session if it exists, otherwise returns None. The current session is defined as the most
        recent session that is less than 12 hours old.
        """
        threshold_for_new_session = 12 # hours
        most_recent_session = self.get_most_recent_session()
        if datetime.now() - most_recent_session.start_time < timedelta(hours=threshold_for_new_session):
            return most_recent_session
        else:
            return None

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
        drinkers = get_drinkers()
        drinkers[self.username] = {
            "password": self.password,
            # Convert datetime to isoformat string
            "dob": self.dob.isoformat(),
            "sex": self.sex,
            "weight": self.weight,
        }
        try:
            with open("databases/users.json", "w") as outfile:
                json.dump(drinkers, outfile)
                print("Saved to database")
        except Exception:
            print("Unable to load database file")
        return drinkers

    def __str__(self):
        return f"Drinker: {self.username}"

class Session:
    id: int
    username: str # Foreign key
    mode: int
    max_alcohol: float
    start_time: datetime
    drive_time: datetime

    def __init__(self, username, mode, max_alcohol, start_time, drive_time, id=None):
        self.id = self._get_new_id() if id is None else id
        self.username = username
        self.mode = mode
        self.max_alcohol = max_alcohol
        self.start_time = start_time
        self.drive_time = drive_time

    def _get_new_id(self):
        """
        Returns the next available id for a session
        """
        sessions = get_all_sessions_from_db()
        if sessions:
            # convert keys to ints and return the max + 1
            return max([int(k) for k in sessions.keys()]) + 1
        else:
            return 1

    def save_to_db(self):
        sessions = get_all_sessions_from_db()
        session = {
            "username": self.username,
            "mode": self.mode,
            "max_alcohol": self.max_alcohol,
            "start_time": self.start_time.isoformat(),
            "drive_time": self.drive_time.isoformat(),
        }
        sessions[self.id] = session
        try:
            with open("databases/sessions.json", "w") as outfile:
                json.dump(sessions, outfile)
                print("Saved to database")
        except Exception:
            print("Unable to load database file")
        return sessions

    def __str__(self):
        return f"Session: {self.id} - {self.username} - {self.mode} - {self.start_time} - {self.max_alcohol} - {self.drive_time}"

@dataclasses.dataclass
class Drink:
    name:str
    type:str
    alcohol_content:float
    ingredients:list
    image_path:str