from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

# Load user data from JSON file
with open('users.json', 'r') as f:
    users = json.load(f)

@app.route('/')
def index():
    return render_template('create_account.html')

@app.route('/register', methods=['POST'])
def register():
    # Load existing user data or create a new file if not exists
    if not os.path.exists('users.json'):
        with open('users.json', 'w') as f:
            f.write('[]')

    # Retrieve form data
    username = request.form.get('username')
    password = request.form.get('password')
    dob = request.form.get('dob')
    height = request.form.get('height')
    weight = request.form.get('weight')
    sex = request.form.get('sex')
    mode = request.form.get('mode')
    start_timer = request.form.get('start_timer')

    # Validate form data
    if not username or not password:
        return 'Username and password are required!'

    # Load existing user data
    with open('users.json', 'r') as f:
        data = json.load(f)

    # Check if username already exists
    if any(user['username'] == username for user in data):
        return 'Username already exists!'

    # Add new user to data
    new_user = {'username': username, 'password': password, 'dob': dob, 'height': height, 'weight': weight, 'sex': sex, 'mode': mode, 'start_timer': start_timer}
    data.append(new_user)

    # Save updated user data to JSON file
    with open('users.json', 'w') as f:
        json.dump(data, f)

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

if __name__ == '__main__':
    app.run(debug=True)