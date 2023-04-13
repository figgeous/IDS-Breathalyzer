from datetime import datetime
import logging
from flask import Flask, render_template, request, redirect, url_for
import json

from pyscripts.bac_calculate import get_drink_recommendations
from pyscripts.objects import Drinker, Session

logging.basicConfig(filename="app.log",
                    filemode='w',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


app = Flask(__name__)

# Load user data from JSON file
with open('databases/users.json', 'r') as f:
    users = json.load(f)

@app.route('/')
def index():
    return render_template('create_account.html')

@app.route('/register', methods=['POST'])
def register():

    # Retrieve form data
    username = request.form.get('username')
    password = request.form.get('password')

    # Validate form data
    if not username or not password:
        return 'Username and password are required!'

    # Check if username already exists
    if Drinker.get_drinker_from_db(username=username):
        return f"Username {username} already exists!"

    new_drinker = Drinker(
        username=username,
        password=password,
        dob=datetime.fromisoformat(request.form.get("dob")),
        sex=request.form.get("sex"),
        weight=request.form.get("weight"),
    )
    new_drinker.save_to_db()

    # Redirect to login page with username
    return redirect('/login?username=' + username)


@app.route('/login', methods=['GET', 'POST'])
def account_login():
    logging.info("Login page accessed")

    # Check if the request method is POST
    if request.method == 'POST':
        logging.info("POST request received")

        # Get form data
        username = request.form['username']
        password = request.form['password']

        logging.info(f"Username: {username}, Password: {password}")

        # Validate username and password against JSON data
        logging.info("Validating username and password")
        drinker = Drinker.get_drinker_from_db(username=username)
        if drinker and drinker.password == password:
            logging.info("Valid username and password")
            return redirect(url_for('account_home', username=username))
        elif drinker and drinker.password != password:
            logging.info("Invalid username and/or password")
            return "Invalid password"

    # Render the login page
    return render_template('login_page.html')


@app.route('/account/home', methods=['GET'])
def account_home():
    username = request.args.get('username')
    logging.info(f"Account page accessed for {username}")

    drinker = Drinker.get_drinker_from_db(username=username)
    current_session = drinker.get_current_session()
    context = {
        "drinker": drinker,
        "current_session": current_session,
    }
    return render_template('account_home.html', **context)

@app.route('/create_new_session', methods=['GET', 'POST'])
def create_new_session():
    """
    Starts a new session for the given username. Returns the new session object.
    """
    username = request.args.get('username')
    if request.method == 'POST':
        new_session = Session(
            username=username,
            mode=request.form.get('mode'),
            max_alcohol=request.form.get('max_alcohol'),
            start_time=datetime.now(),
            drive_time=request.form.get('drive_time', None),
        )
        new_session.save_to_db()
    return render_template('create_new_session.html', username=username)

@app.route('/measure_bac', methods=['GET', 'POST'])
def measure_bac():
    logging.info("Measure_bac page accessed")
    username = request.args.get('username')
    if request.method == 'POST':
        current_bac = request.form.get('current_bac')
        logging.info(f"Post request with current_bac: {current_bac}")
        drinker = Drinker.get_drinker_from_db(username=username)
        recommendations = get_drink_recommendations(
            current_bac=current_bac,
            drinker=drinker,)
        return render_template('recommendation.html', recommendations=recommendations)
    return render_template('input_bac_manually.html', username=username)

@app.route('/recommendation', methods=['GET', 'POST'])
def recommendation():
    logging.info("Recommendation page accessed")
    # logging.info("Recommendation page accessed for user {} with {} request".format(request.form['username'], request.method))

    if request.method == 'POST':
        drinker = Drinker.get_drinker_from_db(username=request.form['username'])
        current_bac = float(request.form['current_bac'])
        mode = request.form['mode']
        max_alcohol = float(request.form['max_alcohol'])
        logging.info("Drinker: {}, current BAC: {}, mode: {}, max alcohol: {}".format(drinker, current_bac, mode, max_alcohol))

        recommendations = get_drink_recommendations(
            current_bac=current_bac,
            drinker=drinker,)

        context = {"recommendations":recommendations}
        logging.info("Recommendations: {}".format(recommendations))
        return render_template('recommendation.html', **context)

    #GET request
    return redirect(url_for('account_login'))

if __name__ == '__main__':
    app.run(debug=True)