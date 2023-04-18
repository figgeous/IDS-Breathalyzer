import json
import logging
import random
import socket
from datetime import datetime
from datetime import timedelta
from io import BytesIO

import qrcode
from flask import Flask
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from pyscripts.objects import Drinker
from pyscripts.objects import get_drink_candidates_for_drive_time
from pyscripts.objects import get_drink_candidates_less_than_max_alcohol
from pyscripts.objects import get_max_potentiometer_value
from pyscripts.objects import Session


logging.basicConfig(
    filename="app.log",
    filemode="w",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)

# Choose the measurement method for the BAC sensor
bac_measurement_method = "manual"  # "potentiometer" or "manual" or "alcohol_sensor"

# Port name for Arduino serial connection. This is likely to be different on your computer.
serial_port_name = "COM7"

app = Flask(__name__)


@app.route("/")
def welcome_page():
    return render_template("welcome_page.html")


@app.route("/qr_code")
def qr_code():
    """
    Returns a QR code image that contains the server URL. By default Flash only listens to requests from the local
    machine, so for the QR code to generate a url that can connect, Flask needs to be run with "--host=0.0.0.0" flag to
    allow it to on all available network interfaces and accept requests from any IP address.
    """
    # Insert the IP address of the server into the QR code
    server_url = "http://192.168.1.121:5000"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(server_url)
    qr.make(fit=True)
    # Create an image in PIL.Image.Image format
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert the image to a byte buffer. Flask can only accept byte or string http responses
    img_buffer = BytesIO()
    img.save(img_buffer, "PNG")
    # Move the pointer to the beginning of the buffer
    img_buffer.seek(0)

    # Create a Flask response object that contains the image
    response = make_response(img_buffer.getvalue())
    # Set the content type to image/png (the default is text/html)
    response.headers["Content-Type"] = "image/png"

    return response


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Creates a new account for a user.
    """
    if request.method == "POST":
        # Retrieve form data
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        # Validate form data
        if not username or not password:
            return "Username and password are required!"

        # Check if username already exists
        if Drinker.get_drinker_from_db(username=username):
            return f"Username {username} already exists!"

        # Create new drinker object
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
    # GET request
    return render_template("create_account.html")


@app.route("/login", methods=["GET", "POST"])
def account_login():
    """
    Logs in a user and redirects them to their account page.
    """
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
    """
    Displays the account home page for the given user.
    """
    logging.info(f"Account page accessed for {user_id}")

    # Get the current drinker (user) from the database
    drinker = Drinker.get_drinker_from_db(user_id=user_id)

    # Get the current session for the user. If there is no current session, then current_session will be None
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
    user_id = request.args.get("user_id", None)

    logging.info(
        "Create new session page accessed, user: {} and method: {}".format(
            user_id, request.method
        )
    )
    if request.method == "POST":
        # Get form data
        user_id = request.form.get("user_id")
        drive_time = request.form.get("drive_time", None)

        # Convert drive time to datetime object
        if drive_time:
            drive_time = datetime.strptime(request.form.get("drive_time"), "%H:%M")
            drive_time = datetime.combine(datetime.today(), drive_time.time())
            # Account for when drive time is in early hours of the morning. If the drive time is before the current time,
            # then the drive time is for the next day...
            if drive_time < datetime.now():
                drive_time += timedelta(days=1)

        # Get the max alcohol level for the session
        max_alcohol = Session.qualitative_to_bac[request.form.get("max_alcohol")]

        # Create new session
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


@app.route("/measure_bac", methods=["GET"])
def measure_bac():
    """
    Redirects to the appropriate page for measuring the user's BAC.
    """
    user_id = request.args.get("user_id", None)
    logging.info("Measure_bac page accessed, user: {}".format(user_id))

    # Route to correct view based on the bac_measurement_method (e.g. "manual", "potentiometer")
    if bac_measurement_method == "potentiometer":
        return redirect(url_for("get_bac_from_potentiometre", user_id=user_id))
    elif bac_measurement_method == "manual":
        return redirect(url_for("measure_bac_manually", user_id=user_id))


@app.route("/measure_bac_manually", methods=["GET", "POST"])
def measure_bac_manually():
    """
    Allows the user to manually enter their BAC. Used only during development.
    """
    user_id = request.args.get("user_id", None)
    logging.info(
        "Measure_bac_manually page accessed, method: {}, user: {}".format(
            request.method, user_id
        )
    )
    if request.method == "POST":
        # Get form data
        current_bac = request.form.get("current_bac")
        user_id = request.form.get("user_id")

        logging.info("Current bac: {}".format(current_bac))

        return redirect(
            url_for(
                "recommendation", user_id=str(user_id), current_bac=str(current_bac)
            )
        )
    # GET request
    return render_template("input_bac_manually.html", user_id=user_id)


@app.route("/get_bac_from_potentiometer", methods=["GET", "POST"])
def get_bac_from_potentiometre():
    """
    Gets the user's BAC from the potentiometer.
    """
    user_id = request.args.get("user_id", None)

    logging.info(
        "Get bac from potentiometer page accessed, method: {}, user: {}".format(
            request.method, user_id
        )
    )

    if request.method == "POST":
        # Get max potentiometer value
        current_bac = get_max_potentiometer_value(serial_port_name=serial_port_name)
        # Round to 3 decimal places and return
        return str(round(current_bac, 3))

    # GET request
    return render_template("input_bac_with_potetiometer.html", user_id=user_id)


@app.route("/<int:user_id>/recommendation/<current_bac>", methods=["GET"])
def recommendation(user_id, current_bac=None):
    """
    Displays drink recommendations for the user.
    """
    logging.info(
        "Recommendation page accessed, user: {}, method: {}, current_bac: {}".format(
            user_id, request.method, current_bac
        )
    )

    # Convert current_bac to float
    current_bac = float(current_bac) if current_bac else None

    # Get drinker and current session
    drinker = Drinker.get_drinker_from_db(user_id=user_id)
    current_session = drinker.get_current_session()

    # Get drink recommendations
    if current_session.drive_time:
        # Based on drive time. The drinker's max alcohol is taken into account.
        recommendations = get_drink_candidates_for_drive_time(
            drinker=drinker, current_bac=current_bac
        )
    else:
        # Based on a user's max alcohol preference (not drive time)
        recommendations = get_drink_candidates_less_than_max_alcohol(
            drinker=drinker, current_bac=current_bac
        )

    # Randomize the order of the recommendations
    random.shuffle(recommendations)

    # Limit the number of recommendations
    number_of_recommendations = 3
    if len(recommendations) > number_of_recommendations:
        recommendations = recommendations[:number_of_recommendations]

    return render_template("recommendation.html", recommendations=recommendations)


if __name__ == "__main__":
    app.run(debug=True)
