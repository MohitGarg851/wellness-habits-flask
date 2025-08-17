from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

# ORM + password hashing
db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    """
    User model for authentication.
    Inherits UserMixin so Flask-Login can manage sessions.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        """Hash password before saving."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Check entered password vs stored hash."""
        return bcrypt.check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User {self.username}>"
