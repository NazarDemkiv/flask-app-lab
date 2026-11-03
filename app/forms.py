from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email

class ContactForm(FlaskForm):
    name = StringField(label="Name", validators=[DataRequired(), Length(min=3, max=30)])
    email = EmailField(label="Email", validators=[DataRequired(), Email()])
    phone = StringField(label="Phone", validators=[DataRequired(), Length(max=10)])
    subject = SelectField(label="Subject", choices=[('cooperation', "Cooperation"), ("question", "Question"), ("offer", "Offer"), ("other", "Other")],
                           validators=[DataRequired()])
    message = TextAreaField(label="Message", validators=[DataRequired(), Length(min=10, max=500)])

    submit = SubmitField(label="Send message")