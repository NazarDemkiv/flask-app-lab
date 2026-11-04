from decimal import Decimal, InvalidOperation

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import DecimalField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange, Optional, ValidationError

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
CATEGORY_CHOICES = [
    ("electronics", "Електроніка"),
    ("clothing", "Одяг"),
    ("books", "Книги"),
    ("home", "Для дому"),
    ("other", "Інше"),
]


def image_content_type(form, field):
    uploaded_file = field.data
    if not uploaded_file:
        return

    stream = uploaded_file.stream
    current_position = stream.tell()
    header = stream.read(8)
    stream.seek(current_position)

    is_png = header.startswith(b"\x89PNG\r\n\x1a\n")
    is_jpeg = header.startswith(b"\xff\xd8\xff")
    if not (is_png or is_jpeg):
        raise ValidationError("Файл не схожий на коректне зображення PNG або JPEG.")


def two_decimal_places(form, field):
    if not field.raw_data or not field.raw_data[0]:
        return
    try:
        raw_price = Decimal(field.raw_data[0])
    except (InvalidOperation, TypeError):
        return  # DecimalField will report an invalid number itself.
    if raw_price.as_tuple().exponent < -2:
        raise ValidationError("Ціна повинна містити не більше двох знаків після коми.")


def image_size_limit(form, field):
    uploaded_file = field.data
    if not uploaded_file:
        return

    stream = uploaded_file.stream
    current_position = stream.tell()
    stream.seek(0, 2)
    file_size = stream.tell()
    stream.seek(current_position)

    if file_size > MAX_IMAGE_SIZE:
        raise ValidationError("Розмір зображення не повинен перевищувати 5 МБ.")


class ProductFieldsForm(FlaskForm):
    name = StringField(
        "Назва товару",
        validators=[DataRequired(), Length(min=3, max=100)],
    )
    content = TextAreaField(
        "Опис",
        validators=[DataRequired(), Length(max=2000)],
    )
    price = DecimalField(
        "Ціна",
        places=2,
        rounding=None,
        validators=[InputRequired(), NumberRange(min=Decimal("0.01")), two_decimal_places],
    )
    category = SelectField(
        "Категорія",
        choices=CATEGORY_CHOICES,
        validators=[DataRequired()],
    )
    quantity = IntegerField(
        "Кількість",
        validators=[InputRequired(), NumberRange(min=0)],
    )


class ProductCreateForm(ProductFieldsForm):
    image = FileField(
        "Зображення (PNG, JPG або JPEG)",
        validators=[FileRequired(), FileAllowed(["png", "jpg", "jpeg"]), image_content_type, image_size_limit],
    )
    submit = SubmitField("Додати товар")


class ProductEditForm(ProductFieldsForm):
    image = FileField(
        "Нове зображення (необов'язково)",
        validators=[Optional(), FileAllowed(["png", "jpg", "jpeg"]), image_content_type, image_size_limit],
    )
    submit = SubmitField("Зберегти зміни")


class DeleteProductForm(FlaskForm):
    submit = SubmitField("Видалити товар")
