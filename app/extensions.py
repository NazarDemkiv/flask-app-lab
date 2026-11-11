from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
migrate = Migrate()
session = Session()
