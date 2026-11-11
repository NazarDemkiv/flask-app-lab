from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db


class Post(db.Model):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    posted: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    category: Mapped[str] = mapped_column(
        Enum("news", "publication", "tech", "other", name="post_category"),
        nullable=False,
        default="other",
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    author: Mapped[str] = mapped_column(
        String(20), nullable=False, default="Anonymous"
    )

    def __repr__(self) -> str:
        return f"<Post {self.id}: {self.title!r}>"
