from datetime import datetime
import logging
from flask import Flask, render_template, request, redirect, url_for
import json

from pyscripts.bac_calculate import get_drink_recommendations
from pyscripts.objects import Drinker

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
    dob = request.form.get('dob')
    weight = request.form.get('weight')
    sex = request.form.get('sex')
    mode = request.form.get('mode')
    start_time = datetime.now()
    max_bac = request.form.get('max_bac')
    drive_time = request.form.get('drive_time', None)

    # Validate form data
    if not username or not password:
        return 'Username and password are required!'

    print([username, password, dob, weight, sex, mode, start_time])

    # Check if username already exists
    if Drinker.get_from_db(username=username):
        return f"Username {username} already exists!"

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
        drinker = Drinker.get_from_db(username=username)
        if drinker and drinker.password == password:
            logging.info("Valid username and password")
            return redirect(url_for('account_home', username=username))
        elif drinker and drinker.password != password:
            logging.info("Invalid username and/or password")
            return "Invalid password"

    # Render the login page
    return render_template('login_page.html')


@app.route('/account/home')
def account_home():
    username = request.args.get('username')
    logging.info(f"Account page accessed for {username}")
    # Render the account_home.html template with username as parameter
    return render_template('account_home.html', username=username)

@app.route('/recommendation', methods=['GET', 'POST'])
def recommendation():
    logging.info("Recommendation page accessed")
    # logging.info("Recommendation page accessed for user {} with {} request".format(request.form['username'], request.method))

    if request.method == 'POST':
        drinker = Drinker.get_from_db(username=request.form['username'])
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