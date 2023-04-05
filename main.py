import datetime
import json

from flask import app
from flask import Flask
from flask import render_template
from flask import request

from objects import Drinker
from pyscripts.crud import get_drinker

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("create_account.html")


@app.route("/register", methods=["POST"])
def register():
    # Load existing user data

    def _check_if_user_exists(username):
        for user in data:
            if user["username"] == username:
                return True
        return False

    # Check if username already exists
    if _check_if_user_exists(request.form["username"]):
        return "Username already exists!"

    # Create Drinker object
    username = request.form["username"]
    password = request.form["password"]
    dob = request.form["dob"]
    mode = request.form["mode"]
    sex = request.form["sex"]
    weight = request.form["weight"]
    start_time = datetime.now()
    max_bac = request.form["max_bac"]
    drive_time = request.form["drive_time"]
    new_drinker = Drinker(
        username=username,
        password=password,
        dob=dob,
        mode=mode,
        sex=sex,
        weight=weight,
        start_time=start_time,
        max_bac=max_bac,
        drive_time=drive_time,
    )
    new_drinker.save_to_db()
    return f"Account created successfully! Username: {username}, Date of Birth: {dob}"


@app.route("/login", methods=["GET"])
def login():
    username = "user123"
    get_drinker(username=username)


if __name__ == "__main__":
    app.run()
