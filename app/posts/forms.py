from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Length


CATEGORY_CHOICES = [
    ("news", "Новина"),
    ("publication", "Публікація"),
    ("tech", "Технології"),
    ("other", "Інше"),
]


class PostForm(FlaskForm):
    title = StringField(
        "Заголовок",
        validators=[DataRequired(message="Вкажіть заголовок."), Length(max=150)],
    )
    content = TextAreaField(
        "Текст публікації",
        validators=[DataRequired(message="Вкажіть текст публікації.")],
    )
    enabled = BooleanField("Показувати публікацію", default=True)
    publish_date = DateTimeLocalField(
        "Дата та час публікації",
        format="%Y-%m-%dT%H:%M",
        default=datetime.now,
        validators=[DataRequired(message="Вкажіть дату та час публікації.")],
    )
    category = SelectField(
        "Категорія", choices=CATEGORY_CHOICES, default="other", validators=[DataRequired()]
    )
    submit = SubmitField("Зберегти")


class DeletePostForm(FlaskForm):
    submit = SubmitField("Так, видалити пост")
