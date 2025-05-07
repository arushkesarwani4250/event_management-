from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, FloatField, IntegerField
from wtforms.validators import DataRequired, NumberRange, Length


class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[
        DataRequired(),
        Length(min=3, max=100)
    ], render_kw={"placeholder": "Enter product name"})

    description = TextAreaField('Description', validators=[
        Length(max=500)
    ], render_kw={"placeholder": "Enter product description", "rows": 4})

    price = FloatField('Price', validators=[
        DataRequired(),
        NumberRange(min=0.01, message="Price must be greater than 0")
    ], render_kw={"placeholder": "0.00"})

    quantity = IntegerField('Quantity', validators=[
        DataRequired(),
        NumberRange(min=0, message="Quantity cannot be negative")
    ], render_kw={"placeholder": "0"})

    image = FileField('Product Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])