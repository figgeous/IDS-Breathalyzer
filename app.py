import json
import logging
import random
import socket
from datetime import datetime
from datetime import timedelta
from io import BytesIO

import qrcode
from flask import Flask, make_response
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
def welcome_page():
    return render_template("welcome_page.html")

@app.route('/qr_code')
def qr_code():
    #get ip address of server
    server_url = 'http://' + socket.gethostbyname(socket.gethostname()) + ':5000'
    logging.info('QR code page accessed')
    server_url = 'http://192.168.1.125:5000'  # Replace with your server URL
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(server_url)
    qr.make(fit=True)
    # Create an image in PIL.Image.Image format
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert the image to a byte buffer. Flask can only accept byte or string http responses
    img_buffer = BytesIO()
    img.save(img_buffer, 'PNG')
    # Move the pointer to the beginning of the buffer
    img_buffer.seek(0)

    # Create a Flask response object that contains the image
    response = make_response(img_buffer.getvalue())
    # Set the content type to image/png (the default is text/html)
    response.headers['Content-Type'] = 'image/png'

    return response

@app.route("/register", methods=["GET", "POST"])
def register():
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


@app.route("/measure_bac", methods=["GET"])
def measure_bac():
    user_id = request.args.get("user_id", None)
    logging.info("Measure_bac page accessed, user: {}".format(user_id))

    if using_arduino:
        pass
        # current_bac = get_bac_from_arduino()
    else:
        return render_template("input_bac_manually.html", user_id=user_id)


@app.route("/<int:user_id>/recommendation", methods=["GET", "POST"])
def recommendation(user_id):
    logging.info("Recommendation page accessed, user: {}, method: {}".format(user_id, request.method))

    if request.method == "POST":
        drinker = Drinker.get_drinker_from_db(user_id=user_id)
        current_bac = float(request.form.get("current_bac"))
        current_session = drinker.get_current_session()

        if current_session.drive_time:
            # Get drink recommendations based on drive time. The drinker's max alcohol is taken into account.
            recommendations = get_drink_candidates_for_drive_time(
                drinker=drinker, current_bac=current_bac
            )
        else:
            # Get drink recommendations based on a user's max alcohol preference (not drive time)
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

    # GET request
    return redirect(url_for("account_login"))


if __name__ == '__main__':
    app.run(debug=True)