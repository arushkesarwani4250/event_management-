from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address'),
        Length(max=120)
    ], render_kw={"placeholder": "your@email.com"})

    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, max=128)
    ], render_kw={"placeholder": "••••••••"})

    remember_me = BooleanField('Remember Me')