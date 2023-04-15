import dataclasses
import json
import logging
import math
from datetime import datetime
from datetime import timedelta


def get_all_drinkers() -> dict[str, dict]:
    try:
        with open("databases/users.json", "r") as infile:
            drinkers = json.load(infile)
    except Exception:
        print("Unable to load database file")
    return drinkers


def get_all_drinks_from_db() -> list["Drink"]:
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


# def get_session_object_from_db(id:int) -> "Session":
#     sessions_from_db = get_all_sessions_from_db()
#     session_dict = sessions_from_db.get(str(id), None)
#     if session_dict:
#         return Session(
#             id=id,
#             user_id=int(session_dict["user_id"]),
#             max_alcohol=float(session_dict["max_alcohol"]),
#             start_time=datetime.fromisoformat(session_dict["start_time"]),
#             drive_time=datetime.fromisoformat(session_dict["drive_time"]),
#         )
#     else:
#         return None


def get_all_sessions_from_db() -> dict[str, dict]:
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
        if drivetime := session_from_db["drive_time"]:
            drivetime = datetime.fromisoformat(drivetime)
        else:
            drivetime = None
        session = Session(
            id=int(session_id),
            user_id=int(session_from_db["user_id"]),
            max_alcohol=float(session_from_db["max_alcohol"]),
            start_time=datetime.fromisoformat(session_from_db["start_time"]),
            drive_time=drivetime,
        )
        sessions.append(session)
    return sessions


def get_drink_candidates_less_than_max_alcohol(
    drinker: "Drinker", current_bac: float
) -> list:
    """
    Returns a list of drinks that are less than the max alcohol for the current session. The list isn't sorted.
    """
    current_session = drinker.get_current_session()
    assert current_session, "No current session"

    all_drinks = get_all_drinks_from_db()

    # Get drinks that are less than the max alcohol for the current session
    candidate_drinks = []
    for drink in all_drinks:
        # print(drink.name, drinker.bac_after_drink(drink=drink, current_bac=current_bac))
        if (
            drinker.bac_after_drink(drink=drink, current_bac=current_bac)
            < current_session.max_alcohol
        ):
            candidate_drinks.append(drink)
    return candidate_drinks


def get_drink_candidates_for_drive_time(drinker: "Drinker", current_bac: float) -> list:
    """
    Returns a list of drinks that are less than the max alcohol for the current session and that will allow the user to
    drive by the drive time of the current session. The list is sorted by alcohol content, highest to lowest. The list
    isn't sorted.
    """
    current_session = drinker.get_current_session()
    drinks_candidates_less_that_max_alcohol = (
        get_drink_candidates_less_than_max_alcohol(
            drinker=drinker, current_bac=current_bac
        )
    )
    candidate_drinks = []
    for drink in drinks_candidates_less_that_max_alcohol:
        bac_after_drink = drinker.bac_after_drink(drink=drink, current_bac=current_bac)
        number_of_seconds_until_can_drive = drinker.number_seconds_until_can_drive(
            current_bac=bac_after_drink
        )
        if (
            number_of_seconds_until_can_drive
            > current_session.seconds_until_drive_time()
        ):
            candidate_drinks.append(drink)
    return candidate_drinks


class Drinker:
    id: int
    username: str
    dob: datetime
    sex: str
    weight: int

    def __init__(self, username, password, dob, sex, weight, id=None):
        self.id = self._get_new_id() if id is None else id
        self.username = username
        self.password = password
        self.dob = dob
        self.sex = sex.lower()
        self.weight = weight

    def _get_new_id(self) -> int:
        """
        Returns the next available id for a drinker
        """
        drinkers = get_all_drinkers()
        if drinkers:
            # convert keys to ints and return the max + 1
            return max([int(k) for k in drinkers.keys()]) + 1
        else:
            return 1

    @staticmethod
    def get_drinker_from_db(
        username: str = None, user_id: int = None
    ) -> "Drinker" or None:
        """
        Returns a Drinker object if the user exists in the database, otherwise returns None
        """
        assert username or user_id, "Must provide either username or user_id"
        all_drinkers = get_all_drinkers()

        selected_id, selected_drinker = None, None
        for id, drinker in all_drinkers.items():
            if (user_id and user_id == int(id)) or (
                username and drinker["username"] == username
            ):
                selected_id, selected_drinker = int(id), drinker
                break

        # If no drinker was found, return None
        if not selected_drinker:
            return None

        assert selected_id

        drinker = Drinker(
            id=int(selected_id),
            username=selected_drinker["username"],
            password=selected_drinker["password"],
            dob=selected_drinker["dob"],
            sex=selected_drinker["sex"],
            weight=int(selected_drinker["weight"]),
        )
        return drinker

    def get_most_recent_session(self) -> "Session" or None:
        sessions_from_db = get_all_session_objects_from_db()
        # Get session for user with most recent start time
        most_recent_session = None
        for session in sessions_from_db:
            if session.user_id != self.id:
                continue
            if most_recent_session is None:
                most_recent_session = session
            elif session.start_time > most_recent_session.start_time:
                most_recent_session = session
        return most_recent_session

    def get_current_session(self) -> "Session" or None:
        """
        Returns the current session if it exists, otherwise returns None. The current session is defined as the most
        recent session that is less than 24 hours old.
        """
        threshold = timedelta(hours=24)

        if most_recent_session := self.get_most_recent_session():
            time_diff = datetime.now() - most_recent_session.start_time
            logging.info(
                f"Most recent session: {most_recent_session}, time diff: {time_diff}"
            )
            if datetime.now() - most_recent_session.start_time < threshold:
                return most_recent_session

        return None

    def bac_after_drink(self, drink: "Drink", current_bac: float) -> float:
        """
        Returns the increase in BAC for a drink, taking current BAC into account
        """
        standard_drinks = (
            drink.alcohol_content / 30
        )  # 30ml of alcohol in a standard drink

        if self.sex == "male":
            a, b = 0.0662, -0.014
        else:  # Female
            a, b = 0.1004, -0.016
        bac_increase_per_drink = a * math.exp(b * self.weight)

        return current_bac + (bac_increase_per_drink * standard_drinks)

    def number_seconds_until_can_drive(self, current_bac: float) -> float:
        """
        Returns the number of seconds until the person can drive, or 0 if they can drive now
        """
        if current_bac <= 0.05:
            return 0

        # Calculate the BAC per drink for the person and the time it takes to metabolize one drink
        if self.sex == "male":
            a1, a2 = 0.0662, -0.014
            b1, b2 = 3.9584, -0.013
        else:  # female
            a1, a2 = 0.1004, -0.016
            b1, b2 = 5.1596, -0.014
        # Amount BAC raises per 30 ml of pure alcohol
        bac_increase_per_drink = a1 * math.exp(a2 * self.weight)
        # Seconds to metabolize 30 ml alc. by weight
        seconds_to_metabolize_one_drink = (b1 * math.exp(b2 * self.weight)) * 3600

        # Calculate the current BAC and time to sober
        drinks_metabolized_per_second = 1 / seconds_to_metabolize_one_drink
        bac_metabolized_per_second = (
            drinks_metabolized_per_second * bac_increase_per_drink
        )
        seconds_to_sober = (current_bac - 0.05) / bac_metabolized_per_second

        return seconds_to_sober

    def save_to_db(self):
        drinkers = get_all_drinkers()
        drinkers[str(self.id)] = {
            "username": self.username,
            "password": self.password,
            # Convert datetime to isoformat string
            "dob": self.dob.isoformat(),
            "sex": self.sex,
            "weight": str(self.weight),
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
    user_id: int  # Foreign key
    max_alcohol: float
    start_time: datetime
    drive_time: datetime
    qualitative_to_bac: dict = {
        "Tipsy": 0.05,
        "Inbetween": 0.07,
        "Drunk": 0.10,
        "Really Drunk": 0.25,
    }
    bac_to_qualitative: dict

    def __init__(self, user_id, start_time, max_alcohol=None, drive_time=None, id=None):
        self.id = self._get_new_id() if id is None else id
        self.user_id = user_id
        self.max_alcohol = max_alcohol
        self.start_time = start_time
        self.drive_time = drive_time
        self.bac_to_qualitative = {v: k for k, v in self.qualitative_to_bac.items()}

    def get_qualitative_max_alcohol(self) -> float:
        """
        Returns the qualitative BAC for the session
        """
        return self.bac_to_qualitative[self.max_alcohol]

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

    def seconds_since_start_time(self) -> int:
        time_diff = datetime.now() - self.start_time
        return round(time_diff.total_seconds() / 60)

    def seconds_until_drive_time(self) -> int or None:
        if self.drive_time:
            time_diff = self.drive_time - datetime.now()
            return round(time_diff.total_seconds() / 3600)
        else:
            return

    def save_to_db(self):
        assert self.user_id, "User id must be set"
        assert self.start_time, "Start time must be set"
        assert self.max_alcohol, "Max alcohol must be set"

        sessions = get_all_sessions_from_db()
        drive_time = self.drive_time.isoformat() if self.drive_time else None
        session = {
            "user_id": self.user_id,
            "max_alcohol": self.max_alcohol,
            "start_time": self.start_time.isoformat(),
            "drive_time": drive_time,
        }
        sessions[str(self.id)] = session
        try:
            with open("databases/sessions.json", "w") as outfile:
                json.dump(sessions, outfile)
                print("Saved to database")
        except Exception:
            print("Unable to load database file")
        return sessions

    def __str__(self):
        return f"Session: {self.id} - {self.user_id} - {self.start_time} - {self.max_alcohol} - {self.drive_time}"


@dataclasses.dataclass
class Drink:
    name: str
    type: str
    alcohol_content: float
    ingredients: list
    image_path: str
