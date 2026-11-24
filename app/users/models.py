from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    # Store a password hash here, not a plain-text password.
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    posts: Mapped[list["Post"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User {self.id}: {self.username!r}>"
