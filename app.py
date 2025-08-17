from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, bcrypt, User, Plan, Activity, UserActivity
import importlib
import os
from forms import LoginForm, RegistrationForm
from werkzeug.security import generate_password_hash, check_password_hash

# ----------------- App Init -----------------
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///wellness_app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "supersecretkey123"

db.init_app(app)
bcrypt.init_app(app)

# ----------------- Login Manager -----------------
login_manager = LoginManager(app)
login_manager.login_view = "home"   # redirect to home if not logged in

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ----------------- Routes -----------------

@app.route("/", methods=["GET", "POST"])
def home():
    # ✅ If already logged in → go straight to dashboard
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    login_form = LoginForm(prefix="login")   # prefix avoids conflicts
    register_form = RegistrationForm(prefix="register")

    # ----- Handle Login -----
    if login_form.validate_on_submit() and login_form.submit.data:
        user = User.query.filter_by(email=login_form.email.data).first()
        if user and check_password_hash(user.password, login_form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password", "danger")

    # ----- Handle Register -----
    elif register_form.validate_on_submit() and register_form.submit.data:
        if User.query.filter_by(email=register_form.email.data).first():
            flash("Email already registered!", "danger")
        else:
            hashed_password = generate_password_hash(register_form.password.data, method="pbkdf2:sha256")
            new_user = User(
                username=register_form.username.data,
                email=register_form.email.data,
                password=hashed_password
            )
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
    return redirect(url_for("home"))   # ✅ not "/"

# Dashboard
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html",
                           plan=current_user.plan,
                           activities=current_user.user_activities)
# View Plan
@app.route("/view_plan/<int:plan_id>")
@login_required
def view_plan(plan_id):
    plan = Plan.query.get(plan_id)
    if not plan:
        flash("Plan not found.", "danger")
        return redirect(url_for("dashboard"))
    return render_template("view_plan.html", plan=plan, activities=plan.activities)

# Plans list
@app.route("/plans")
@login_required
def plans():
    plans = Plan.query.all()
    return render_template("plans.html", plans=plans)

# Select plan
@app.route("/select_plan/<int:plan_id>", methods=["GET", "POST"])
@login_required
def select_plan(plan_id):
    plan = Plan.query.get(plan_id)
    activities = plan.activities

    if request.method == "POST":
        selected = request.form.getlist("activities")
        levels = {a_id: request.form.get(f"level_{a_id}") for a_id in selected}

        # clear old selections
        UserActivity.query.filter_by(user_id=current_user.id).delete()

        for a_id in selected:
            ua = UserActivity(user_id=current_user.id,
                              activity_id=int(a_id),
                              level=levels[a_id])
            db.session.add(ua)

        # lock plan
        current_user.plan = plan
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

                    plan = Plan(name=module.plan_name)
                    db.session.add(plan)
                    db.session.commit()

                    for act in module.activities:
                        activity = Activity(
                            name=act["name"],
                            level1=act["level1"],
                            level2=act["level2"],
                            level3=act["level3"],
                            plan=plan
                        )
                        db.session.add(activity)
                    db.session.commit()

    app.run(debug=True)
