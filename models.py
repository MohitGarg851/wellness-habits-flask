from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date

db = SQLAlchemy()

# ----------------------------
# User Model
# ----------------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

    # FK → one plan per user
    plan_id = db.Column(db.Integer, db.ForeignKey("plan.id"))
    plan_start_date = db.Column(db.Date, nullable=True)

    # Relationships
    plan = db.relationship("Plan", backref="users")   # a plan can have many users
    user_activities = db.relationship("UserActivity", backref="user", lazy=True)
    daily_logs = db.relationship("DailyLog", backref="user", lazy=True)

  # ------------------------
# Plan Model
# ------------------------
class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # thresholds
    min_activities = db.Column(db.Integer, default=3)
    max_activities = db.Column(db.Integer, default=6)
    min_points = db.Column(db.Integer, default=30)
    max_points = db.Column(db.Integer, default=90)

    # A plan has many activities
    activities = db.relationship("Activity", backref="plan", lazy=True)

# ------------------------
# Activity Model
# ------------------------
class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Activity belongs to a plan
    plan_id = db.Column(db.Integer, db.ForeignKey("plan.id"))

    # Levels
    level1 = db.Column(db.String(100))
    level2 = db.Column(db.String(100))
    level3 = db.Column(db.String(100))
    recommended = db.Column(db.String(10))   # e.g. "L2"

    # One activity can be chosen by many users
    user_activities = db.relationship("UserActivity", backref="activity", lazy=True)
    daily_logs = db.relationship("DailyLog", backref="activity", lazy=True)

# ------------------------
# UserActivity Model (Join Table)
# ------------------------
class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # FKs
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey("activity.id"), nullable=False)

    # Store which level was selected (L1/L2/L3)
    level = db.Column(db.String(10), nullable=False)

# ------------------------
# DailyLog Model
# ------------------------
class DailyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey("activity.id"), nullable=False)
    log_date = db.Column(db.Date, default=date.today, nullable=False)
    status = db.Column(db.String(20), default="not_done")  # "done", "skipped"
    notes = db.Column(db.Text, nullable=True)