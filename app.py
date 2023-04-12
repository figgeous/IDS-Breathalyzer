from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for
import json
import os

from pyscripts.objects import Drinker

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
    height = request.form.get('height')
    weight = request.form.get('weight')
    sex = request.form.get('sex')
    mode = request.form.get('mode')
    start_time = request.form.get('start_timer')

    # Validate form data
    if not username or not password:
        return 'Username and password are required!'


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
        # max_bac=max_bac,
        # drive_time=drive_time,
    )
    new_drinker.save_to_db()

    # Redirect to login page with username
    return redirect('/login?username=' + username)


@app.route('/login', methods=['GET', 'POST'])
def account_login():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']

        # Validate username and password against JSON data
        for user in users:
            if user['username'] == username and user['password'] == password:
                # Redirect to account.html upon successful login
                return redirect(url_for('account_home'))
        # Show error message for invalid login
        return "Invalid username or password"
    else:
        # Render the login form for GET request
        return render_template('account_login.html')

@app.route('/account/home')
def account_home():
    # Get the username from the URL parameter
    username = request.args.get('username')

    # Render the account.html template with username as parameter
    return render_template('account.html', username=username)

@app.route('/account/drinker')
def account_result():

    return render_template('drinker.html')

if __name__ == '__main__':
    app.run(debug=True)