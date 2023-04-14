from datetime import datetime, timedelta
import logging
from flask import Flask, render_template, request, redirect, url_for
import json

# from pyscripts.bac_calculate import get_drink_recommendations
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


@app.route('/account/<int:user_id>', methods=['GET'])
def account_home(user_id):
    logging.info(f"Account page accessed for {user_id}")

    drinker = Drinker.get_drinker_from_db(user_id=user_id)
    current_session = drinker.get_current_session()
    context = {
        "drinker": drinker,
        "current_session": current_session,
    }
    return render_template('account_home.html', **context)

@app.route('/create_new_session/<int:user_id>', methods=['GET', 'POST'])
def create_new_session(user_id):
    """
    Starts a new session for the given user
    """
    logging.info("Create new session page accessed, user: {}".format(user_id))
    if request.method == 'POST':
        drive_time = request.form.get("drive_time", None)
        if drive_time:
            drive_time = datetime.strptime(request.form.get('drive_time'), '%H:%M')
            drive_time = datetime.combine(datetime.today(), drive_time.time())
            # Account for when drive time is in early hours of the morning
            if drive_time < datetime.now():
                drive_time += timedelta(days=1)

        subjective_bac = {
            "1":0.03, # Tipsy
            "2":0.06, # Inbetween
            "3": 0.010, # Drunk
            "4": 0.020, # Blackout
        }
        max_alcohol = subjective_bac[request.form.get('max_alcohol')]
        new_session = Session(
            user_id=user_id,
            max_alcohol=request.form.get('max_alcohol'),
            start_time=datetime.now(),
            drive_time=drive_time,
        )
        new_session.save_to_db()
        return redirect(url_for('account_home', user_id=user_id))
    return render_template('create_new_session.html', user_id=user_id)

@app.route('/<int:user_id>/measure_bac', methods=['GET', 'POST'])
def measure_bac(user_id):
    logging.info("Measure_bac page accessed, user: {}".format(user_id))
    if request.method == 'POST':
        current_bac = request.form.get('current_bac')
        logging.info(f"Post request with current_bac: {current_bac}")
        drinker = Drinker.get_drinker_from_db(user_id=user_id)
        # recommendations = get_drink_recommendations(
        #     current_bac=current_bac,
        #     drinker=drinker,)
        recommendations = []
        return render_template('recommendation.html', recommendations=recommendations)
    return render_template('input_bac_manually.html', user_id=user_id)

@app.route('/<int:user_id>/recommendation', methods=['GET', 'POST'])
def recommendation(user_id):
    logging.info("Recommendation page accessed, user: {}".format(user_id))
    # logging.info("Recommendation page accessed for user {} with {} request".format(request.form['username'], request.method))

    if request.method == 'POST':
        drinker = Drinker.get_drinker_from_db(user_id=request.form['user_id'])
        current_bac = float(request.form['current_bac'])
        max_alcohol = float(request.form['max_alcohol'])
        logging.info("Drinker: {}, current BAC: {}, max alcohol: {}".format(drinker, current_bac, max_alcohol))

        # recommendations = get_drink_recommendations(
        #     current_bac=current_bac,
        #     drinker=drinker,)
        recommendations = []
        context = {"recommendations":recommendations}
        logging.info("Recommendations: {}".format(recommendations))
        return render_template('recommendation.html', **context)

    #GET request
    return redirect(url_for('account_login'))

if __name__ == '__main__':
    app.run(debug=True)