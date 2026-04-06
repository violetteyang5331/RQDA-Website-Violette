from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint("auth", __name__)

# Dancer dictionaries for each level
TEST_USERS = [
    
]

TEEN_DANCERS = [
    {"first_name": "Violette", "last_name": "Yang", "birthday": "02-09", "account": False},
    {"first_name": "Test", "last_name": "User", "birthday": "01-01", "account": False}
]

ADULT_DANCERS = [
    # Add adult dancers here
]

JUNIOR_DANCERS = [
    # Add junior dancers here
]

MINI_DANCERS = [
    # Add mini dancers here
]

DANCER_LISTS = {
    "test": TEST_USERS,
    "teen": TEEN_DANCERS,
    "adult": ADULT_DANCERS,
    "junior": JUNIOR_DANCERS,
    "mini": MINI_DANCERS
}

# Check if a dancer exists in the official list
def is_valid_dancer(level, first_name, last_name, birthday):
    dancers = DANCER_LISTS.get(level, [])
    for dancer in dancers:
        if (dancer["first_name"] == first_name and
            dancer["last_name"] == last_name and
            dancer["birthday"] == birthday):
            return True
    return False

# Check if a dancer already has an account
def has_account(level, first_name, last_name, birthday):
    dancers = DANCER_LISTS.get(level, [])
    for dancer in dancers:
        if (dancer["first_name"] == first_name and
            dancer["last_name"] == last_name and
            dancer["birthday"] == birthday):
            return dancer.get("account", False)
    return False

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            flash("Logged in successfully!", category="success")
            login_user(user, remember=True)
            return redirect(url_for("views.home"))
        else:
            flash("Invalid email or password.", category="error")

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

        # Validation checks
        if not rqda_level:
            flash("Please select an RQDA level.", category="error")
        elif not email or len(email) < 4 or "@" not in email:
            flash("Please enter a valid email address.", category="error")
        elif not first_name or len(first_name) < 2:
            flash("First name must be at least 2 characters.", category="error")
        elif not last_name or len(last_name) < 2:
            flash("Last name must be at least 2 characters.", category="error")
        elif len(password1) < 6:
            flash("Password must be at least 6 characters.", category="error")
        elif password1 != password2:
            flash("Passwords must match.", category="error")
        else:
            # Check duplicates: email or dancer identity
            user_email_exists = User.query.filter_by(email=email).first()
            dancer_has_account = has_account(rqda_level, first_name, last_name, birthday)

            if user_email_exists or dancer_has_account:
                flash("An account with this email or dancer info already exists.", category="error")
            elif not is_valid_dancer(rqda_level, first_name, last_name, birthday):
                flash("Not a valid dancer, please check your information.", category="error")
            else:
                # Create new user
                new_user = User(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    rqda_level=rqda_level,
                    password=generate_password_hash(password1, method="pbkdf2:sha256")
                )
                db.session.add(new_user)
                db.session.commit()

                # Mark dancer as having an account
                dancers = DANCER_LISTS[rqda_level]
                for dancer in dancers:
                    if (dancer["first_name"] == first_name and
                        dancer["last_name"] == last_name and
                        dancer["birthday"] == birthday):
                        dancer["account"] = True
                        break

                flash("Account created!", category="success")
                login_user(new_user, remember=True)
                return redirect(url_for("views.home"))

    return render_template("sign_up.html", user=current_user)

@auth.route("/about-us")
def about_us():
    return render_template("about_us.html", user=current_user)

@auth.route("/meet-the-team")
def meet_the_team():
    return render_template("meet_the_team.html", user=current_user)

@auth.route("/schedule")
@login_required
def schedule():
    return render_template("schedule.html", user=current_user)

@auth.route("/gallery")
def gallery():
    return render_template("gallery.html", user=current_user)