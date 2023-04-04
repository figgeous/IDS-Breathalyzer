from flask import Flask, render_template, request, app
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('create_account.html')

@app.route('/register', methods=['POST'])
def register():
    # Load existing user data
    import os

    if not os.path.exists('users.json'):
        with open('users.json', 'w') as f:
            f.write('[]')

    with open('users.json', 'r') as f:
        data = json.load(f)

    username = request.form['username']
    password = request.form['password']
    dob = request.form['dob']

    # Check if username already exists
    if any(user['username'] == username for user in data):
        return 'Username already exists!'

    # Add new user to data
    data.append({'username': username, 'password': password, 'dob': dob})
    with open('users.json', 'w') as f:
        json.dump(data, f)

    return f'Account created successfully! Username: {username}, Date of Birth: {dob}'

if __name__ == '__main__':
    app.run()
