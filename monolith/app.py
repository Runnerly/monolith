from stravalib import Client
import functools
import os
from flask import Flask, render_template, request, redirect
from flask_login import (LoginManager, login_user, logout_user, login_required,
                         current_user, current_app)
from monolith.database import db, User, Run
from monolith.forms import UserForm, LoginForm


app = Flask(__name__)
app.config['WTF_CSRF_SECRET_KEY'] = 'A SECRET KEY'
app.config['SECRET_KEY'] = 'ANOTHER ONE'
app.config['STRAVA_CLIENT_ID'] = os.environ['STRAVA_CLIENT_ID']
app.config['STRAVA_CLIENT_SECRET'] = os.environ['STRAVA_CLIENT_SECRET']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/runnerly'


def _strava_auth_url():
    client = Client()
    client_id = app.config['STRAVA_CLIENT_ID']
    redirect = 'http://127.0.0.1:5000/strava_auth'
    url = client.authorization_url(client_id=client_id,
                                   redirect_uri=redirect)
    return url


@app.route('/strava_auth')
@login_required
def _strava_auth():
    code = request.args.get('code')
    client = Client()
    xc = client.exchange_code_for_token
    access_token = xc(client_id=app.config['STRAVA_CLIENT_ID'],
                      client_secret=app.config['STRAVA_CLIENT_SECRET'],
                      code=code)
    current_user.strava_token = access_token
    db.session.add(current_user)
    db.session.commit()
    return redirect('/')


@app.route('/')
def index():
    if current_user is not None:
        runs = db.session.query(Run).filter(Run.runner_id == current_user.id)
    else:
        runs = None
    strava_auth_url = _strava_auth_url()
    return render_template("index.html", runs=runs,
                           strava_auth_url=strava_auth_url)


@app.route('/users')
def users():
    users = db.session.query(User)
    return render_template("users.html", users=users)


def admin_required(func):
    @functools.wraps(func)
    def _admin_required(*args, **kw):
        admin = current_user.is_authenticated and current_user.is_admin
        if not admin:
            return current_app.login_manager.unauthorized()
        return func(*args, **kw)
    return _admin_required


@app.route('/create_user', methods=['GET', 'POST'])
@admin_required
def create_user():
    form = UserForm()
    if request.method == 'POST':

        if form.validate_on_submit():
            new_user = User()
            form.populate_obj(new_user)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/users')

    return render_template('create_user.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email, password = form.data['email'], form.data['password']
        q = db.session.query(User).filter(User.email == email)
        user = q.first()
        if user is not None and user.authenticate(password):
            login_user(user)
            return redirect('/')
    return render_template('login.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect('/')


login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    if user is not None:
        user._authenticated = True
    return user


if __name__ == '__main__':
    db.init_app(app)
    login_manager.init_app(app)
    db.create_all(app=app)

    with app.app_context():
        q = db.session.query(User).filter(User.email == 'tarek@ziade.org')
        user = q.first()
        if user is None:
            tarek = User()
            tarek.email = 'tarek@ziade.org'
            tarek.is_admin = True
            tarek.set_password('ok')
            db.session.add(tarek)
            db.session.commit()

    app.run()
