import dataclasses
import json
import logging
import math
import time
from datetime import datetime
from datetime import timedelta

import serial


def get_max_potentiometer_value(serial_port_name: str) -> float:
    """
    Connects to the serial port and collects data for 5 seconds. Returns the maximum value
    :param serial_port_name: The name of the serial port
    """
    # Connect to serial port. This is likely to be different on your computer.
    serial_port_name = "COM7"
    ser = serial.Serial(serial_port_name, 9600)

    # Loop that runs for five seconds while data is collected. Decode and remove whitespace
    data = []
    for i in range(0, 50):
        # Read data from serial port
        data.append(float(ser.readline().decode().strip()))
        # Wait for 0.1 seconds
        time.sleep(0.1)
    # Close serial port
    ser.close()

    # When turned up all the way the potentiometer reads 4095. This is the maximum value.
    maximum_possible_potentio_value = 4095
    maximum_possible_bac = 0.3  # 0.3% BAC, which is close to comatosed
    maximum_measured = max(data)
    conversion_to_bac = (
        maximum_possible_bac / maximum_possible_potentio_value
    ) * maximum_measured
    return conversion_to_bac


def get_all_drinkers() -> dict[str, dict]:
    """
    Returns a dictionary of all drinkers from the database.
    """
    try:
        with open("databases/users.json", "r") as infile:
            drinkers = json.load(infile)
    except Exception:
        logging.exception("Unable to load database file")
    return drinkers


def get_all_drinks_from_db() -> list["Drink"]:
    """
    Returns a list of Drink objects from the database.
    """
    try:
        with open("databases/beverages.json", "r") as infile:
            beverages_from_db = json.load(infile)
    except Exception as e:
        logging.exception("Unable to load database file", e)

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


def get_all_sessions_from_db() -> dict[str, dict]:
    """
    Returns a dictionary of all sessions from the database.
    """
    try:
        with open("databases/sessions.json", "r") as infile:
            sessions_from_db = json.load(infile)
    except Exception as e:
        logging.error("Unable to load database file", e)
    return sessions_from_db


def get_all_session_objects_from_db() -> list["Session"]:
    """
    Returns a list of Session objects from the database.
    """
    # Get all sessions from database
    sessions_from_db = get_all_sessions_from_db()

    # Create session objects
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
    # Get current session
    current_session = drinker.get_current_session()

    # Get all drinks from database
    all_drinks = get_all_drinks_from_db()

    # Get drinks that give a rise in BAC less than the max alcohol for the current session.
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
    # Get drinks that give a rise in BAC less than the max alcohol for the current session.
    current_session = drinker.get_current_session()
    drinks_candidates_less_that_max_alcohol = (
        get_drink_candidates_less_than_max_alcohol(
            drinker=drinker, current_bac=current_bac
        )
    )

    # Take list from above and select drinks that will allow the user to drive by the drive time of the current session.
    candidate_drinks = []
    for drink in drinks_candidates_less_that_max_alcohol:
        bac_after_drink = drinker.bac_after_drink(drink=drink, current_bac=current_bac)
        number_of_seconds_until_can_drive = drinker.number_seconds_until_can_drive(
            current_bac=bac_after_drink
        )
        # If the number of seconds until the user can drive is less than the number of seconds until the drive time of the
        # current session, then the drink is a candidate.
        if (
            number_of_seconds_until_can_drive
            > current_session.seconds_until_drive_time()
        ):
            candidate_drinks.append(drink)
    return candidate_drinks


class Drinker:
    """
    Corresponds to a user in the database. The user can have multiple sessions.
    """

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
        # Get all drinkers from the database
        drinkers = get_all_drinkers()

        # If there are any drinkers, return the max id + 1
        if drinkers:
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

        # Get all drinkers from the database
        all_drinkers = get_all_drinkers()

        # Find the drinker with the matching username or id
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

        # Create and return a Drinker object
        drinker = Drinker(
            id=int(selected_id),
            username=selected_drinker["username"],
            password=selected_drinker["password"],
            dob=selected_drinker["dob"],
            sex=selected_drinker["sex"],
            weight=int(selected_drinker["weight"]),
        )
        return drinker

    def get_current_session(self) -> "Session" or None:
        """
        Gets the current session for the user. If the user has a session that started less than 24 hours ago, it returns
        that session. Otherwise, it returns None.
        """
        #
        sessions_from_db = get_all_session_objects_from_db()

        # Get session for user with most recent start time
        most_recent_session = None
        # Iterate through all sessions in the database and find the most recent session for the user
        for session in sessions_from_db:
            if session.user_id != self.id:
                continue
            if most_recent_session is None:
                most_recent_session = session
            elif session.start_time > most_recent_session.start_time:
                most_recent_session = session

        # If the most recent session is less than 24 hours ago, return it. Otherwise, return None
        threshold = timedelta(hours=24)
        if most_recent_session:
            time_diff = datetime.now() - most_recent_session.start_time

            if datetime.now() - most_recent_session.start_time < threshold:
                return most_recent_session

        return None

    def bac_after_drink(self, drink: "Drink", current_bac: float) -> float:
        """
        Returns the drinkers BAC after drinking the drink, taking into account the current BAC
        """
        standard_drinks = (
            drink.alcohol_content / 30
        )  # 30ml of alcohol is considered a standard drink in our app

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
        if current_bac <= 0.05:  # 0.05 is the legal limit
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
        """
        Saves the user to the database
        """
        # Load the database
        drinkers = get_all_drinkers()
        # Add the user to the database
        drinkers[str(self.id)] = {
            "username": self.username,
            "password": self.password,
            # Convert datetime to isoformat string
            "dob": self.dob.isoformat(),
            "sex": self.sex,
            "weight": str(self.weight),
        }
        # Save the database
        try:
            with open("databases/users.json", "w") as outfile:
                json.dump(drinkers, outfile)
                logging.info("Saved to database")
        except Exception:
            logging.exception("Unable to load database file")
        return drinkers

    def __str__(self):
        return f"Drinker: {self.username}"


class Session:
    """
    Represents a session of drinking for a user
    """

    qualitative_to_bac: dict = {
        "Tipsy": 0.05,
        "Inbetween": 0.07,
        "Drunk": 0.10,
        "Really Drunk": 0.25,
    }
    bac_to_qualitative: dict

    def __init__(
        self,
        user_id: int,
        start_time: datetime,
        max_alcohol: float = None,
        drive_time: datetime = None,
        id: int = None,
    ):
        # If no id is provided, get a new one
        self.id = self._get_new_id() if id is None else id
        self.user_id = user_id
        self.max_alcohol = max_alcohol
        self.start_time = start_time
        self.drive_time = drive_time
        # Create a dict that maps bac to qualitative. Keys and values are swapped.
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

    def seconds_until_drive_time(self) -> int or None:
        """
        Returns the number of seconds until the drive time, or None if there is no drive time
        """
        if self.drive_time:
            time_diff = self.drive_time - datetime.now()
            return round(time_diff.total_seconds() / 3600)
        else:
            return

    def save_to_db(self) -> dict[str, dict] or None:
        """
        Saves the session to the database
        """
        # Check that all required fields are set
        assert self.user_id, "User id must be set"
        assert self.start_time, "Start time must be set"
        assert self.max_alcohol, "Max alcohol must be set"

        # Get all sessions from the database
        sessions = get_all_sessions_from_db()
        # Convert datetime to isoformat string
        drive_time = self.drive_time.isoformat() if self.drive_time else None
        # Create a dict for the session
        session = {
            "user_id": self.user_id,
            "max_alcohol": self.max_alcohol,
            "start_time": self.start_time.isoformat(),
            "drive_time": drive_time,
        }
        # Add the session to the dict of sessions
        sessions[str(self.id)] = session

        # Save the sessions to the database
        try:
            with open("databases/sessions.json", "w") as outfile:
                json.dump(sessions, outfile)
                logging.info("Saved to database")
        except Exception:
            logging.exception("Unable to load database file")
        return sessions

    def __str__(self):
        return f"Session: {self.id} - {self.user_id} - {self.start_time} - {self.max_alcohol} - {self.drive_time}"


@dataclasses.dataclass
class Drink:
    """
    Represents a drink
    """

    name: str
    type: str
    alcohol_content: float
    ingredients: list
    image_path: str
