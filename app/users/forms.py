import re

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError

from ..extensions import db
from .models import User


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(), Length(min=4, max=80),
            Regexp(r"^[A-Za-z0-9_.]+$", message="Username може містити лише літери, цифри, крапки та підкреслення."),
        ],
    )
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, message="Пароль має містити щонайменше 6 символів.")])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password", message="Паролі повинні збігатися.")]
    )
    submit = SubmitField("Зареєструватися")

    def validate_username(self, field):
        username = field.data.strip()
        if db.session.scalar(db.select(User).where(User.username == username)):
            raise ValidationError("Це ім'я користувача вже зайняте.")

    def validate_email(self, field):
        email = field.data.strip().lower()
        if db.session.scalar(db.select(User).where(User.email == email)):
            raise ValidationError("Користувач із такою електронною поштою вже зареєстрований.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")
