import json
import logging
from datetime import datetime
from datetime import timedelta

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from pyscripts.objects import Drinker
from pyscripts.objects import get_drink_candidates_for_drive_time
from pyscripts.objects import get_drink_candidates_less_than_max_alcohol
from pyscripts.objects import Session

# from pyscripts.bac_calculate import get_drink_recommendations

logging.basicConfig(
    filename="app.log",
    filemode="w",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)

# Set to True if using Arduino. This will allow the app to read data from the Arduino rather that the user inputting
# data manually.
using_arduino = False

app = Flask(__name__)

# Load user data from JSON file
with open("databases/users.json", "r") as f:
    users = json.load(f)


@app.route("/")
def create_account():
    return render_template("create_account.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # Retrieve form data
    username = request.form.get("username").strip()
    password = request.form.get("password").strip()

    # Validate form data
    if not username or not password:
        return "Username and password are required!"

    # Check if username already exists
    if Drinker.get_drinker_from_db(username=username):
        return f"Username {username} already exists!"

    new_drinker = Drinker(
        username=username,
        password=password,
        dob=datetime.strptime(request.form.get("dob"), "%Y-%m-%d"),
        sex=request.form.get("sex").strip(),
        weight=int(request.form.get("weight")),
    )
    new_drinker.save_to_db()

    # Redirect to login page with username
    return redirect("/login?username=" + username)


@app.route("/login", methods=["GET", "POST"])
def account_login():
    logging.info("Login page accessed with method: {}".format(request.method))

    # Check if the request method is POST
    if request.method == "POST":
        # Get form data
        username = request.form["username"]
        password = request.form["password"]

        logging.info(f"Username: {username}, Password: {password}")

        # Validate username and password against JSON data
        drinker = Drinker.get_drinker_from_db(username=username)
        if drinker and drinker.password == password:
            logging.info("Valid username and password")
            return redirect(url_for("account_home", user_id=drinker.id))
        elif drinker and drinker.password != password:
            logging.info("Invalid username and/or password")
            return "Invalid password"

    # Render the login page
    return render_template("login_page.html")


@app.route("/account/<int:user_id>", methods=["GET"])
def account_home(user_id):
    logging.info(f"Account page accessed for {user_id}")

    drinker = Drinker.get_drinker_from_db(user_id=user_id)

    current_session = drinker.get_current_session()
    logging.info(f"Drinker: {drinker.username}, current session: {current_session}")

    context = {
        "drinker": drinker,
        "current_session": current_session,
    }
    return render_template("account_home.html", **context)


@app.route("/create_new_session", methods=["GET", "POST"])
def create_new_session():
    """
    Starts a new session for the given user
    """
    # get arg from url
    user_id = request.args.get("user_id", None)

    logging.info(
        "Create new session page accessed, user: {} and method: {}".format(
            user_id, request.method
        )
    )
    if request.method == "POST":
        user_id = request.form.get("user_id")
        assert user_id, "User id not found in POST request"

        drive_time = request.form.get("drive_time", None)
        if drive_time:
            drive_time = datetime.strptime(request.form.get("drive_time"), "%H:%M")
            drive_time = datetime.combine(datetime.today(), drive_time.time())
            # Account for when drive time is in early hours of the morning
            if drive_time < datetime.now():
                drive_time += timedelta(days=1)

        max_alcohol = Session.qualitative_to_bac[request.form.get("max_alcohol")]
        new_session = Session(
            user_id=user_id,
            max_alcohol=max_alcohol,
            start_time=datetime.now(),
            drive_time=drive_time,
        )
        new_session.save_to_db()
        logging.info("New session created for user: {}".format(user_id))
        return redirect(url_for("account_home", user_id=user_id))

    # GET request
    logging.info("GET request for create new session page")
    return render_template("create_new_session.html", user_id=user_id)


@app.route("/measure_bac", methods=["GET", "POST"])
def measure_bac():
    # get arg from url
    user_id = request.args.get("user_id", None)
    print("user_id: {}".format(user_id))

    logging.info("Measure_bac page accessed, user: {}".format(user_id))
    if request.method == "POST":
        user_id = int(request.form.get("user_id"))
        print(request.form)
        print("Post request user_id: {}".format(user_id))
        if current_bac := request.form.get("current_bac"):
            current_bac = float(current_bac)
        else:
            return "No current BAC found in POST request"
        current_bac = float(request.form.get("current_bac"))
        logging.info(f"Post request with current_bac: {current_bac}")

        drinker = Drinker.get_drinker_from_db(user_id=user_id)

        current_session = drinker.get_current_session()

        if current_session.drive_time:
            recommendations = get_drink_candidates_for_drive_time(
                drinker=drinker, current_bac=current_bac
            )
        else:
            recommendations = get_drink_candidates_less_than_max_alcohol(
                drinker=drinker, current_bac=current_bac
            )

        number_of_recommendations = 3
        if len(recommendations) > number_of_recommendations:
            recommendations = recommendations[:number_of_recommendations]

        return render_template("recommendation.html", recommendations=recommendations)
    return render_template("input_bac_manually.html", user_id=user_id)


@app.route("/<int:user_id>/recommendation", methods=["GET", "POST"])
def recommendation(user_id):
    logging.info("Recommendation page accessed, user: {}".format(user_id))
    # logging.info("Recommendation page accessed for user {} with {} request".format(request.form['username'], request.method))

    if request.method == "POST":
        drinker = Drinker.get_drinker_from_db(user_id=request.form["user_id"])
        current_bac = float(request.form["current_bac"])
        max_alcohol = float(request.form["max_alcohol"])
        logging.info(
            "Drinker: {}, current BAC: {}, max alcohol: {}".format(
                drinker, current_bac, max_alcohol
            )
        )

        # recommendations = get_drink_recommendations(
        #     current_bac=current_bac,
        #     drinker=drinker,)
        recommendations = []
        context = {"recommendations": recommendations}
        logging.info("Recommendations: {}".format(recommendations))
        return render_template("recommendation.html", **context)

    # GET request
    return redirect(url_for("account_login"))


if __name__ == "__main__":
    app.run(debug=True)
