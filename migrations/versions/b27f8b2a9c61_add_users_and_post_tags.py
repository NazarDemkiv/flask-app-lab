"""Add users and many-to-many tags for posts.

Revision ID: b27f8b2a9c61
Revises: 84c830a515ce
Create Date: 2026-11-24

"""
from alembic import op
import sqlalchemy as sa


revision = "b27f8b2a9c61"
down_revision = "84c830a515ce"
branch_labels = None
depends_on = None


def upgrade():
    # Create the User table first, because posts.user_id references it.
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("username", name="uq_users_username"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )

    # Add a nullable FK temporarily so existing posts can be assigned an author.
    op.add_column("posts", sa.Column("user_id", sa.Integer(), nullable=True))

    connection = op.get_bind()
    posts_table = sa.table(
        "posts",
        sa.column("id", sa.Integer()),
        sa.column("author", sa.String(length=20)),
        sa.column("user_id", sa.Integer()),
    )
    users_metadata = sa.MetaData()
    users_table = sa.Table(
        "users",
        users_metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=80)),
        sa.Column("email", sa.String(length=120)),
        sa.Column("password", sa.String(length=255)),
    )

    old_authors = connection.execute(
        sa.select(posts_table.c.author).distinct().order_by(posts_table.c.author)
    ).scalars().all()

    # Preserve author names from the old string column as User records.
    used_usernames = set()
    for index, old_author in enumerate(old_authors, start=1):
        username = str(old_author or "").strip() or f"legacy_user_{index}"
        if username in used_usernames:
            username = f"{username[:65]}_{index}"
        used_usernames.add(username)
        result = connection.execute(
            users_table.insert().values(
                username=username,
                email=f"legacy-{index}@example.invalid",
                # This placeholder is intentionally not a usable password hash.
                password="!legacy-account-disabled!",
            )
        )
        user_id = result.inserted_primary_key[0]

        if old_author is None:
            condition = posts_table.c.author.is_(None)
        else:
            condition = posts_table.c.author == old_author

        connection.execute(
            posts_table.update().where(condition).values(user_id=user_id)
        )

    # All old posts now have a User. Make the FK required and remove the old text field.
    with op.batch_alter_table("posts", schema=None) as batch_op:
        batch_op.alter_column(
            "user_id",
            existing_type=sa.Integer(),
            nullable=False,
        )
        batch_op.create_foreign_key(
            "fk_posts_user_id_users",
            "users",
            ["user_id"],
            ["id"],
        )
        batch_op.drop_column("author")

    # Tag table and association table implement Post <-> Tag many-to-many.
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_tags"),
        sa.UniqueConstraint("name", name="uq_tags_name"),
    )
    op.create_table(
        "post_tags",
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["post_id"], ["posts.id"], name="fk_post_tags_post_id_posts"
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"], ["tags.id"], name="fk_post_tags_tag_id_tags"
        ),
        sa.PrimaryKeyConstraint("post_id", "tag_id", name="pk_post_tags"),
    )


def downgrade():
    op.drop_table("post_tags")
    op.drop_table("tags")

    connection = op.get_bind()
    posts_table = sa.table(
        "posts",
        sa.column("id", sa.Integer()),
        sa.column("user_id", sa.Integer()),
        sa.column("author", sa.String(length=20)),
    )
    users_table = sa.table(
        "users",
        sa.column("id", sa.Integer()),
        sa.column("username", sa.String(length=80)),
    )

    # Restore the author text from User.username before removing the relationship.
    with op.batch_alter_table("posts", schema=None) as batch_op:
        batch_op.add_column(sa.Column("author", sa.String(length=20), nullable=True))

    rows = connection.execute(
        sa.select(posts_table.c.id, users_table.c.username).select_from(
            posts_table.join(users_table, posts_table.c.user_id == users_table.c.id)
        )
    ).all()
    for post_id, username in rows:
        connection.execute(
            posts_table.update()
            .where(posts_table.c.id == post_id)
            .values(author=str(username)[:20])
        )

    with op.batch_alter_table("posts", schema=None) as batch_op:
        batch_op.alter_column(
            "author",
            existing_type=sa.String(length=20),
            nullable=False,
        )
        batch_op.drop_constraint("fk_posts_user_id_users", type_="foreignkey")
        batch_op.drop_column("user_id")

    op.drop_table("users")
