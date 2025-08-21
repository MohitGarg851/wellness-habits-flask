from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Plan, Activity, UserActivity, DailyLog
import importlib
import os
from forms import LoginForm, RegistrationForm
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, timedelta


# ----------------- App Init -----------------
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///wellness_app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "supersecretkey123"

db.init_app(app)
bcrypt = Bcrypt(app)


# ----------------- Login Manager -----------------
login_manager = LoginManager(app)
login_manager.login_view = "home"   # redirect to home if not logged in

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ----------------- Routes -----------------
@app.route("/", methods=["GET", "POST"])
def home():
    # If already logged in → go straight to dashboard
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    login_form = LoginForm()
    register_form = RegistrationForm()

    # ----- Handle Login -----
    if request.method == "POST" and "login-submit" in request.form:
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password", "danger")

    # ----- Handle Register -----
    elif request.method == "POST" and "register-submit" in request.form:
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
        elif password != confirm_password:
            flash("Passwords must match!", "danger")
        else:
            hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("home"))

    return render_template("home.html", login_form=login_form, register_form=register_form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("home"))


# ----------------- Dashboard -----------------
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    today = date.today()

    # --- Handle Daily Form Submission ---
    if request.method == "POST":
        # User-selected date (can be backdate)
        log_date_str = request.form.get("log_date")
        if log_date_str:
            log_date = date.fromisoformat(log_date_str)
        else:
            log_date = today

        # Loop over all activities in user's plan
        for ua in current_user.user_activities:
            status = request.form.get(f"activity_{ua.activity.id}", "not_done")

            existing_log = DailyLog.query.filter_by(
                user_id=current_user.id,
                activity_id=ua.activity.id,
                log_date=log_date
            ).first()

            if existing_log:
                existing_log.status = status
            else:
                new_log = DailyLog(
                    user_id=current_user.id,
                    activity_id=ua.activity.id,
                    log_date=log_date,
                    status=status
                )
                db.session.add(new_log)

        db.session.commit()
        flash(f"Log saved for {log_date}!", "success")
        return redirect(url_for("dashboard"))

    # --- Prepare Summary Logs (from plan start date to today)
    summary = {}
    if current_user.plan_start_date:
        all_days = [current_user.plan_start_date + timedelta(days=i)
                    for i in range((today - current_user.plan_start_date).days + 1)]

        for d in all_days:
            logs = DailyLog.query.filter_by(user_id=current_user.id, log_date=d).all()
            summary[d] = {log.activity_id: log.status for log in logs}

    return render_template(
        "dashboard.html",
        plan=current_user.plan,
        activities=current_user.user_activities,
        summary=summary,
        today=today
    )



# ----------------- Plans -----------------
@app.route("/view_plan/<int:plan_id>")
@login_required
def view_plan(plan_id):
    plan = Plan.query.get(plan_id)
    if not plan:
        flash("Plan not found.", "danger")
        return redirect(url_for("dashboard"))
    return render_template("view_plan.html", plan=plan, activities=plan.activities)


@app.route("/plans")
@login_required
def plans():
    plans = Plan.query.all()
    return render_template("plans.html", plans=plans)


@app.route("/select_plan/<int:plan_id>", methods=["GET", "POST"])
@login_required
def select_plan(plan_id):
    plan = Plan.query.get(plan_id)
    activities = plan.activities

    if request.method == "POST":
        selected = request.form.getlist("activities")
        start_date = request.form.get("plan_start_date")

        levels = {}
        total_points = 0
        for a_id in selected:
            level = request.form.get(f"level_{a_id}") or "L2"
            levels[a_id] = level

            if level == "L1":
                total_points += 5
            elif level == "L2":
                total_points += 10
            elif level == "L3":
                total_points += 15

        # Threshold validations
        if len(selected) < plan.min_activities or \
           (plan.max_activities and len(selected) > plan.max_activities):
            flash(f"Select between {plan.min_activities} and {plan.max_activities} activities.", "danger")
            return redirect(url_for("select_plan", plan_id=plan.id))

        if total_points < plan.min_points or \
           (plan.max_points and total_points > plan.max_points):
            flash(f"Your plan must have at least {plan.min_points} points.", "danger")
            return redirect(url_for("select_plan", plan_id=plan.id))

        # Save selections
        UserActivity.query.filter_by(user_id=current_user.id).delete()
        for a_id in selected:
            ua = UserActivity(
                user_id=current_user.id,
                activity_id=int(a_id),
                level=levels[a_id]
            )
            db.session.add(ua)

        # Assign plan + start date
        current_user.plan = plan
        if start_date:
            from datetime import datetime
            current_user.plan_start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

        db.session.commit()
        flash("Plan locked successfully!", "success")
        return redirect(url_for("my_plan"))

    return render_template("select_plan.html", plan=plan, activities=activities)


@app.route("/my_plan")
@login_required
def my_plan():
    if not current_user.plan:
        flash("No plan selected yet.", "warning")
        return redirect(url_for("plans"))
    return render_template("my_plan.html", plan=current_user.plan, activities=current_user.user_activities)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html",
                           user=current_user,
                           plan=current_user.plan,
                           activities=current_user.user_activities)


# ----------------- Daily Log (per activity, old route) -----------------
@app.route("/daily_log/<int:activity_id>", methods=["POST"])
@login_required
def daily_log(activity_id):
    status = request.form.get("status")
    notes = request.form.get("notes")

    existing_log = DailyLog.query.filter_by(
        user_id=current_user.id,
        activity_id=activity_id,
        log_date=date.today()
    ).first()

    if existing_log:
        existing_log.status = status
        existing_log.notes = notes
    else:
        new_log = DailyLog(
            user_id=current_user.id,
            activity_id=activity_id,
            log_date=date.today(),
            status=status,
            notes=notes
        )
        db.session.add(new_log)

    db.session.commit()
    flash("Log saved successfully!", "success")
    return redirect(url_for("dashboard"))


# ---------------- Main ----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # load plans if empty
        if not Plan.query.first():
            plans_folder = "plans"
            for filename in os.listdir(plans_folder):
                if filename.endswith(".py"):
                    module_name = filename[:-3]
                    module = importlib.import_module(f"plans.{module_name}")

                    plan = Plan(
                        name=module.plan_name,
                        min_activities=getattr(module, "min_activities", 1),
                        max_activities=getattr(module, "max_activities", None),
                        min_points=getattr(module, "min_points", 0),
                        max_points=getattr(module, "max_points", None),
                    )
                    db.session.add(plan)
                    db.session.commit()

                    for act in module.activities:
                        activity = Activity(
                            name=act["name"],
                            level1=act["level1"],
                            level2=act["level2"],
                            level3=act["level3"],
                            recommended=act.get("recommended"),
                            plan=plan
                        )
                        db.session.add(activity)
                    db.session.commit()

    app.run(debug=True)
