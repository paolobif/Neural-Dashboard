from flask import Flask, request, jsonify, render_template, redirect, session, flash
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from functools import wraps
import boto3


app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = '123'
socketio = SocketIO(app)
CORS(app)

ec2 = boto3.resource('ec2')  # Inits connection to aws.
instance_id = 'i-0463a4a99fdb1a7f9'


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


def getInstanceState(ec2_id):
    instance = ec2.Instance(id=ec2_id)
    status = instance.state['Name']
    print(status)
    return status


def updateInstaceState(ec2_id):
    """Creates instance connection and will update
    the state depending on the existing state.

    Args:
        ec2_id (str): ec2 instance id.
    """
    instance = ec2.Instance(id=ec2_id)
    status = instance.state['Name']
    print(status)

    if status == "running":
        instance.stop()
    elif status == "stopping":
        pass
    elif status == "stopped":
        instance.start()
    elif status == "starting":
        pass

    return status


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
    ec2_state = getInstanceState(ec2_id=instance_id)
    print(ec2_state)
    if request.method == 'POST':
        if request.form.get('state') == "update_state":
            updateInstaceState(instance_id)
            print("post")
            return render_template('index.html', state=ec2_state)

        elif request.form.get('refresh') == "refresh":
            return render_template('index.html', state=ec2_state)

        else:  # allows for support for other post requests.
            return render_template('index.html', state=ec2_state)

    if request.method == 'GET':
        return render_template('index.html', state=ec2_state)


if __name__ == '__main__':

    app.run(host="0.0.0.0", port="5000", debug=True)