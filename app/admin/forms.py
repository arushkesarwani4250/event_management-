from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length


class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=50)
    ])

    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])

    role = SelectField('Role', choices=[
        ('admin', 'Administrator'),
        ('vendor', 'Vendor'),
        ('user', 'Regular User')
    ], validators=[DataRequired()])

    active = BooleanField('Active Account')