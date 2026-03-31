from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint("auth", __name__)

TEEN_DANCERS = [
    {"first_name": "Violette", "last_name": "Yang", "birthday":"02:09", "account":False}
    ]

def match(level, firstName, lastName, birthday):
    if level == "adult":
        pass
    if level == "teen":
        for i in range(1, len(TEEN_DANCERS)):
            if firstName == TEEN_DANCERS[i]["first_name"] and lastName == TEEN_DANCERS[i]["last_name"]and birthday == TEEN_DANCERS[i]["birthday"]:
                TEEN_DANCERS[i]["account"] = True
                return True
            else:
                return False
    if level == "junior":
        pass
    if level == "mini":
        pass
    
def has_acc(level, firstName, lastName, birthday):
    if level == "adult":
        pass
    if level == "teen":
        for i in range(1, len(TEEN_DANCERS)):
            if firstName == TEEN_DANCERS[i]["first_name"] and lastName == TEEN_DANCERS[i]["last_name"]and birthday == TEEN_DANCERS[i]["birthday"]:
                if TEEN_DANCERS[i]["account"] == True:
                    return True
                else:
                    return False
            else:
                return False
    if level == "junior":
        pass
    if level == "mini":
        pass

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully!", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect password, try again.", category="error")
        else:
            flash("Email does not exist.", category="error")
        
    return render_template("login.html", user=current_user)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        rqda_level = request.form.get("rqda_level")
        email = request.form.get("email")
        first_name = request.form.get("firstName")
        last_name = request.form.get("lastName")
        birthday = request.form.get("birthday_md")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        
        user = User.query.filter_by(email=email).first()
        validity = match(rqda_level, first_name, last_name, birthday)
        
        '''
        if user:
            flash("Email already exists.", category="error")
        elif rqda_level == "":
            flash("Please enter an RQDA level.", category="error")
        elif len(email) < 4:
            flash("Email must be greater than 3 characters.", category="error")
        elif len(first_name) < 2:
            flash("First name must be greater than 1 character.", category="error")
        elif password1 != password2:
            flash("Passwords must match.", category="error")
        elif len(password1) < 7:
            flash("Password must be at least 7 characters.", category="error")
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method="pbkdf2:sha256"))
            db.session.add(new_user)
            db.session.commit()
            flash("Account created!", category="success")
            login_user(user, remember=True)
            return redirect(url_for("views.home"))
        '''
        
        if user or has_acc(rqda_level, first_name, last_name, birthday):
            flash("Account already exists.", category="error")
        elif validity == False:
            flash("Not a valid dancer, please check your information.", category="error")
        elif password1 != password2:
            flash("Passwords must match.", category="error")
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method="pbkdf2:sha256"))
            db.session.add(new_user)
            db.session.commit()
            flash("Account created!", category="success")
            login_user(user, remember=True)
            return redirect(url_for("views.home"))
    
    return render_template("sign_up.html", user=current_user)