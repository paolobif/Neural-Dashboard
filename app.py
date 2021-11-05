from flask import Flask, request, jsonify, render_template, redirect, session, flash
from flask_cors import CORS
from flask_socketio import SocketIO
from functools import wraps
import boto3
# import argparse

from dash_utils import fetch_instance_data, updateInstaceState


app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = '123testest'
socketio = SocketIO(app)
CORS(app)

ec2 = boto3.resource('ec2')  # Inits connection to aws.
client = boto3.client('ec2')

# instance_id = 'i-0463a4a99fdb1a7f9'

# Add arguments
# parser = argparse.ArgumentParser(description='Process some integers.')
# parser.add_argument('ec2_id', metavar='N', type=str, nargs='+',
                    # help='id for the ec2 instance')
# args = parser.parse_args()
#
# Instance constants
# instance_id = args.ec2_id[0]
# instance = ec2.Instance(id=instance_id)
# public_ip = "http://" + instance.public_ip_address
instances = fetch_instance_data()  # From dash_utils... instance id: state, ip.


# Basic single use... can be expanded to unclude db of users.
class User():
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_admin(self):
        return True

    def get_id(self):
        return self.id


# ADD users:
users = []
users.append(User(user_id=1, username='root', password='root'))


# Ensures login to access dashboard.
def login_required(f):
    wraps(f)

    def wrap(*args, **kwargs):
        if session['authorized']:
            return f(*args, **kwargs)
        else:
            flash("You are not logged in.")
            return redirect('/')

    return(wrap)


# -------- Sockets -------- #


@socketio.on('connect')
def connect():
    print("connected")


@socketio.on('disconnect')
def disconnect():
    print("disconnecting")
    session['authorized'] = False


# -------- API ROUTES -------- #

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)
        session['authorized'] = False
        username = request.form['username']
        password = request.form['password']

        user = [n for n in users if n.username == username]
        if user:
            user = user[0]  # fetches the user
        else:
            flash("Username not found...")
            return redirect('/')

        # handle login.
        if user.password == password:
            session['user_id'] = user.id
            session['authorized'] = True
            return redirect('/dashboard')

        return redirect('/')
    if request.method == 'GET':
        return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    # ec2_state = getInstanceState(ec2_id=instance_id)
    # instances = fetch_instance_data()
    # print(instances)
    # if request.method == 'POST':
    #     instance_id = request.form.get('instance_id')
    #     if request.form.get('state') == "update_state":
    #         updateInstaceState(instance_id)
    #         print("post")
    #         return render_template('index.html', instance=instances)

    #     elif request.form.get('refresh') == "refresh":
    #         return render_template('index.html', instances=instances)

    #     else:  # allows for support for other post requests.
    #         return render_template('index.html', instances=instances)

    if request.method == 'GET':
        return render_template('index.html')
        # , instances=instances)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000", debug=True)
