import functools
from flask import Flask, render_template, jsonify, request, redirect
from flask_login import (LoginManager, login_user, logout_user, login_required,
                         current_user)
from monolith.database import db, User
from monolith.forms import UserForm, LoginForm


app = Flask(__name__)
app.config['WTF_CSRF_SECRET_KEY'] = 'wddq'
app.config['SECRET_KEY'] = 'wqdwqf'


@app.route('/')
def index():
    return render_template("index.html")


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
        tarek = User()
        tarek.email = 'tarek@ziade.org'
        tarek.is_admin = True
        tarek.set_password('ok')
        db.session.add(tarek)
        db.session.commit()

    app.run()
