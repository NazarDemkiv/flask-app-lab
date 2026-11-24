import unittest

from app import create_app
from app.extensions import db
from app.posts.models import Post, Tag
from app.users.models import User


class PostRelationshipTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.app_context.pop()

    def test_one_user_can_have_many_posts(self):
        user = User(username="user1", email="user1@example.com", password="hash")
        post1 = Post(title="Post 1", content="Text 1", user=user)
        post2 = Post(title="Post 2", content="Text 2", user=user)
        db.session.add_all([post1, post2])
        db.session.commit()

        self.assertEqual(len(user.posts), 2)
        self.assertIs(post1.user, user)
        self.assertIs(post2.user, user)

    def test_posts_and_tags_have_many_to_many_relationship(self):
        user = User(username="user1", email="user1@example.com", password="hash")
        tech = Tag(name="Tech")
        art = Tag(name="Art")
        post1 = Post(title="Post 1", content="Text 1", user=user, tags=[tech, art])
        post2 = Post(title="Post 2", content="Text 2", user=user, tags=[tech])
        db.session.add_all([post1, post2])
        db.session.commit()

        self.assertEqual({tag.name for tag in post1.tags}, {"Tech", "Art"})
        self.assertEqual({post.title for post in tech.posts}, {"Post 1", "Post 2"})


if __name__ == "__main__":
    unittest.main()
