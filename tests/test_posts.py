import unittest
from datetime import datetime

from app import create_app
from app.extensions import db
from app.posts.models import Post, Tag
from app.users.models import User


class PostCrudTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        self.user1 = User(
            username="Nazar",
            email="nazar@example.com",
            password="test-password-hash",
        )
        self.user2 = User(
            username="Olena",
            email="olena@example.com",
            password="test-password-hash",
        )
        self.tag1 = Tag(name="Tech")
        self.tag2 = Tag(name="Science")
        db.session.add_all([self.user1, self.user2, self.tag1, self.tag2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.app_context.pop()

    @staticmethod
    def post_data(author_id, tag_ids=None, **overrides):
        data = {
            "title": "Тестова публікація",
            "content": "Це текст тестової публікації для перевірки CRUD-операцій.",
            "enabled": "y",
            "publish_date": "2026-11-11T10:30",
            "category": "news",
            "author_id": str(author_id),
            "tags": [str(tag_id) for tag_id in (tag_ids or [])],
        }
        data.update(overrides)
        return data

    def create_post(self, **overrides):
        data = self.post_data(self.user1.id, [self.tag1.id], **overrides)
        return self.client.post("/post/create", data=data, follow_redirects=False)

    def test_create_post_with_selected_author_and_tags(self):
        response = self.create_post()
        self.assertEqual(response.status_code, 302)

        post = db.session.scalar(db.select(Post))
        self.assertIsNotNone(post)
        self.assertEqual(post.title, "Тестова публікація")
        self.assertEqual(post.user.username, "Nazar")
        self.assertEqual([tag.name for tag in post.tags], ["Tech"])
        self.assertEqual(post.category, "news")
        self.assertTrue(post.is_active)
        self.assertEqual(post.posted, datetime(2026, 11, 11, 10, 30))

    def test_author_and_tags_are_loaded_in_add_form(self):
        response = self.client.get("/post/create")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Nazar", html)
        self.assertIn("Olena", html)
        self.assertIn("Tech", html)
        self.assertIn("Science", html)

    def test_list_shows_active_posts_sorted_by_date_descending(self):
        older = Post(
            title="Старіший пост",
            content="Текст старішого поста",
            posted=datetime(2026, 11, 10, 10, 0),
            category="other",
            is_active=True,
            user=self.user1,
        )
        newer = Post(
            title="Новіший пост",
            content="Текст новішого поста",
            posted=datetime(2026, 11, 11, 10, 0),
            category="tech",
            is_active=True,
            user=self.user2,
        )
        hidden = Post(
            title="Неактивний пост",
            content="Цей пост не має відображатися у списку",
            is_active=False,
            user=self.user1,
        )
        db.session.add_all([older, newer, hidden])
        db.session.commit()

        response = self.client.get("/post")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertLess(html.index("Новіший пост"), html.index("Старіший пост"))
        self.assertNotIn("Неактивний пост", html)
        self.assertIn("Nazar", html)
        self.assertIn("postdefault.jpg", html)

    def test_post_detail_displays_author_and_tags(self):
        self.create_post()
        post = db.session.scalar(db.select(Post))
        response = self.client.get(f"/post/{post.id}")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Це текст тестової публікації", html)
        self.assertIn("Nazar", html)
        self.assertIn("Tech", html)
        self.assertIn("news", html)

    def test_update_post_changes_fields_author_and_tags(self):
        self.create_post()
        post = db.session.scalar(db.select(Post))

        edit_page = self.client.get(f"/post/{post.id}/update")
        self.assertEqual(edit_page.status_code, 200)
        self.assertIn("Тестова публікація", edit_page.get_data(as_text=True))
        self.assertIn("2026-11-11T10:30", edit_page.get_data(as_text=True))

        response = self.client.post(
            f"/post/{post.id}/update",
            data=self.post_data(
                self.user2.id,
                [self.tag2.id],
                title="Оновлений заголовок",
                content="Оновлений текст публікації.",
                enabled="",
                publish_date="2026-11-12T12:00",
                category="publication",
            ),
        )
        self.assertEqual(response.status_code, 302)
        db.session.refresh(post)
        self.assertEqual(post.title, "Оновлений заголовок")
        self.assertEqual(post.content, "Оновлений текст публікації.")
        self.assertFalse(post.is_active)
        self.assertEqual(post.posted, datetime(2026, 11, 12, 12, 0))
        self.assertEqual(post.category, "publication")
        self.assertEqual(post.user.username, "Olena")
        self.assertEqual([tag.name for tag in post.tags], ["Science"])

    def test_delete_requires_confirmation_and_removes_post(self):
        self.create_post()
        post = db.session.scalar(db.select(Post))

        confirmation = self.client.get(f"/post/{post.id}/delete")
        self.assertEqual(confirmation.status_code, 200)
        self.assertIn("Видалити пост?", confirmation.get_data(as_text=True))

        response = self.client.post(f"/post/{post.id}/delete", data={})
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(db.session.get(Post, post.id))

    def test_invalid_post_is_not_created(self):
        data = self.post_data(self.user1.id, title="", content="")
        response = self.client.post("/post/create", data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(db.session.scalar(db.select(db.func.count()).select_from(Post)), 0)

    def test_missing_post_returns_404(self):
        self.assertEqual(self.client.get("/post/999").status_code, 404)
        self.assertEqual(self.client.get("/post/999/update").status_code, 404)
        self.assertEqual(self.client.get("/post/999/delete").status_code, 404)


if __name__ == "__main__":
    unittest.main()
