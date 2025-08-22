from wtforms import Form, StringField, PasswordField, SubmitField, HiddenField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo


# ------------------------
# Login Form
# ------------------------
class LoginForm(Form):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


# ------------------------
# Registration Form
# ------------------------
class RegistrationForm(Form):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")]
    )
    submit = SubmitField("Register")


# ------------------------
# Daily Log Form (Optional)
# ------------------------
class DailyLogForm(Form):
    activity_id = HiddenField("Activity ID")
    status = SelectField(
        "Status",
        choices=[
            ("not_done", "❌ Not Done"),
            ("L1", "Level 1"),
            ("L2", "Level 2"),
            ("L3", "Level 3")
        ],
        validators=[DataRequired()]
    )
    notes = TextAreaField("Notes (optional)")
    submit = SubmitField("Save Log")

class EditProfileForm(Form):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    bio = TextAreaField("Bio", validators=[Length(max=250)])
    submit = SubmitField("Save Changes")
