from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User, Schedule
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from PIL import Image

import os
import random

auth = Blueprint("auth", __name__)

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
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        # Validation checks
        if not rqda_level:
            flash("Please select an RQDA level.", category="error")
        elif not email or len(email) < 4 or "@" not in email:
            flash("Please enter a valid email address.", category="error")
        elif not first_name or len(first_name) < 1:
            flash("First name must be at least 2 characters.", category="error")
        elif not last_name or len(last_name) < 1:
            flash("Last name must be at least 2 characters.", category="error")
        elif len(password1) < 5:
            flash("Password must be at least 6 characters.", category="error")
        elif password1 != password2:
            flash("Passwords must match.", category="error")
        else:
            # Check duplicates: email or dancer identity
            user_email_exists = User.query.filter_by(email=email).first()

            if user_email_exists:
                flash("An account with this email already exists.", category="error")
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

@auth.route("/schedule", methods=["GET", "POST"])
def schedule():
    password_map = {
        os.getenv("ADULT_PASSWORD"): 0,
        os.getenv("TEEN_PASSWORD"): 1,
        os.getenv("JUNIOR_PASSWORD"): 2,
        os.getenv("MINI_PASSWORD"): 3,
        os.getenv("ROSE_PASSWORD"): 4
    }

    level_map = {
        0: "Adult",
        1: "Teen",
        2: "Junior",
        3: "Mini"
    }

    if request.method == "POST":
        entered = request.form.get("schedule_password")

        # Handle edit form submission (Rose view)
        if request.form.get("class_level"):
            class_level = request.form.get("class_level")
            content = request.form.get("content")
            s = Schedule.query.filter_by(class_level=class_level).first()
            if s:
                s.content = content
            else:
                s = Schedule(class_level=class_level, content=content)
                db.session.add(s)
            db.session.commit()
            flash("Schedule updated!", "success")

        elif entered and entered in password_map:
            session["password_index"] = password_map[entered]
            # flash("Access granted", "success")
        else:
            session["password_index"] = -1
            flash("Incorrect password", "error")

    password_index = session.get("password_index", -1)

    schedule = None
    if password_index in level_map:
        schedule = Schedule.query.filter_by(class_level=level_map[password_index]).first()

    schedules = Schedule.query.all() if password_index == 4 else []

    return render_template(
        "schedule.html",
        user=current_user,
        password_index=password_index,
        schedule=schedule,
        schedules=schedules
    )

@auth.route('/delete-schedule/<int:id>', methods=['POST'])
def delete_schedule(id):
    schedule = Schedule.query.get(id)
    if schedule:
        db.session.delete(schedule)
        db.session.commit()
    return redirect(url_for('auth.schedule'))  # back to schedule, not edit_schedule

@auth.route("/reset_schedule_access", methods=["POST"])
def reset_schedule_access():
    session["password_index"] = -1
    # flash("Access reset", "success")
    return redirect(url_for("auth.schedule"))

@auth.route("/edit_schedule", methods=["GET", "POST"])
def edit_schedule():
    if request.method == "POST":
        class_level = request.form.get("class_level")
        content = request.form.get("content")

        schedule = Schedule.query.filter_by(class_level=class_level).first()

        if schedule:
            schedule.content = content
        else:
            schedule = Schedule(class_level=class_level, content=content)
            db.session.add(schedule)

        db.session.commit()
        flash("Schedule updated!", "success")

    schedules = Schedule.query.all()
    schedules_json = [
        {"id": s.id, "class_level": s.class_level, "content": s.content}
        for s in schedules
    ]
    return render_template("edit_schedule.html", schedules=schedules, schedules_json=schedules_json, user=current_user)

@auth.route("/gallery")
def gallery():
    images = [f"gallery/gallery{i}.webp" for i in range(1, 56)]
    random.shuffle(images)
    return render_template("gallery.html", user=current_user, images=images)