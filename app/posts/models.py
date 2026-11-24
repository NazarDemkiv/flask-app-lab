from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db


# Association table for the many-to-many relationship between Post and Tag.
post_tags = db.Table(
    "post_tags",
    db.Column("post_id", db.Integer, db.ForeignKey("posts.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
)


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


    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="posts")

    # A post can have many tags, and each tag can belong to many posts.
    tags: Mapped[list["Tag"]] = relationship(
        secondary=post_tags,
        back_populates="posts",
    )

    def __repr__(self) -> str:
        return f"<Post {self.id}: {self.title!r}>"


class Tag(db.Model):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    posts: Mapped[list[Post]] = relationship(
        secondary=post_tags,
        back_populates="tags",
    )

    def __repr__(self) -> str:
        return f"<Tag {self.id}: {self.name!r}>"
