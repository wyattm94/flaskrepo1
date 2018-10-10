from flask_wtf import flaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,TextAreaField
from wtforms.validators import DataRequired,ValidationError,Email, EqualTo,Length