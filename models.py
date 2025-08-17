from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # Relationship → one user has one selected plan
    plan_id = db.Column(db.Integer, db.ForeignKey("plan.id"))
    plan = db.relationship("Plan", backref="users")

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Plan(db.Model):
    """
    Predefined plans like Plan A, Plan B
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


class Activity(db.Model):
    """
    Activities under a plan, with 3 levels
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    level1 = db.Column(db.String(100))
    level2 = db.Column(db.String(100))
    level3 = db.Column(db.String(100))

    plan_id = db.Column(db.Integer, db.ForeignKey("plan.id"))
    plan = db.relationship("Plan", backref="activities")


class UserActivity(db.Model):
    """
    Activities chosen by a user
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    activity_id = db.Column(db.Integer, db.ForeignKey("activity.id"))
    level = db.Column(db.String(20))  # chosen level (L1, L2, L3)

    user = db.relationship("User", backref="user_activities")
    activity = db.relationship("Activity")
