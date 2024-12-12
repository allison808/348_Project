from flask import Blueprint, render_template, redirect, url_for, request, flash
from .import db
from .models import User
from flask_login import login_user, logout_user, login_required, current_user

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")

        user = User.query.filter_by(email=email).first()
        if user:
            if user.username == username:
                flash("Logged in!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Information is incorrect.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html")


@auth.route("/sign-up", methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        email  = request.form.get("email")
        username = request.form.get("username")

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()
        
        if email_exists:
            flash('Email is already in use.', category='error')
        elif username_exists:
            flash('Username is already in use.', category='error')
        elif len(email) < 4:
            flash("Email is invalid.", category='error')
        else:
            new_user = User(email=email, username=username)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User created!')
            return redirect(url_for('views.home'))

    return render_template("signup.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))