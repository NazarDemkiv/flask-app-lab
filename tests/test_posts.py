import unittest
from datetime import datetime

from app import create_app
from app.extensions import db
from app.posts.models import Post


class PostCrudTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.app_context.pop()

    @staticmethod
    def post_data(**overrides):
        data = {
            "title": "Тестова публікація",
            "content": "Це текст тестової публікації для перевірки CRUD-операцій.",
            "enabled": "y",
            "publish_date": "2026-11-11T10:30",
            "category": "news",
        }
        data.update(overrides)
        return data

    def create_post(self, **overrides):
        return self.client.post(
            "/post/create", data=self.post_data(**overrides), follow_redirects=False
        )

    def test_create_post_with_anonymous_author(self):
        response = self.create_post()
        self.assertEqual(response.status_code, 302)

        post = db.session.scalar(db.select(Post))
        self.assertIsNotNone(post)
        self.assertEqual(post.title, "Тестова публікація")
        self.assertEqual(post.author, "Anonymous")
        self.assertEqual(post.category, "news")
        self.assertTrue(post.is_active)
        self.assertEqual(post.posted, datetime(2026, 11, 11, 10, 30))

    def test_logged_in_user_becomes_post_author(self):
        with self.client.session_transaction() as user_session:
            user_session["username"] = "Nazar"

        self.create_post()
        post = db.session.scalar(db.select(Post))
        self.assertEqual(post.author, "Nazar")

    def test_list_shows_active_posts_sorted_by_date_descending(self):
        older = Post(
            title="Старіший пост",
            content="Текст старішого поста",
            posted=datetime(2026, 11, 10, 10, 0),
            category="other",
            is_active=True,
        )
        newer = Post(
            title="Новіший пост",
            content="Текст новішого поста",
            posted=datetime(2026, 11, 11, 10, 0),
            category="tech",
            is_active=True,
        )
        hidden = Post(
            title="Неактивний пост",
            content="Цей пост не має відображатися у списку",
            is_active=False,
        )
        db.session.add_all([older, newer, hidden])
        db.session.commit()

        response = self.client.get("/post")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertLess(html.index("Новіший пост"), html.index("Старіший пост"))
        self.assertNotIn("Неактивний пост", html)
        self.assertIn("postdefault.jpg", html)

    def test_post_detail_displays_full_content_and_metadata(self):
        self.create_post()
        post = db.session.scalar(db.select(Post))

        response = self.client.get(f"/post/{post.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Це текст тестової публікації", response.get_data(as_text=True))
        self.assertIn("Anonymous", response.get_data(as_text=True))
        self.assertIn("news", response.get_data(as_text=True))

    def test_update_post_changes_all_form_fields(self):
        self.create_post()
        post = db.session.scalar(db.select(Post))

        edit_page = self.client.get(f"/post/{post.id}/update")
        self.assertEqual(edit_page.status_code, 200)
        self.assertIn("Тестова публікація", edit_page.get_data(as_text=True))
        self.assertIn("2026-11-11T10:30", edit_page.get_data(as_text=True))

        response = self.client.post(
            f"/post/{post.id}/update",
            data=self.post_data(
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
        response = self.create_post(title="", content="")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(db.session.scalar(db.select(db.func.count()).select_from(Post)), 0)

    def test_missing_post_returns_404(self):
        self.assertEqual(self.client.get("/post/999").status_code, 404)
        self.assertEqual(self.client.get("/post/999/update").status_code, 404)
        self.assertEqual(self.client.get("/post/999/delete").status_code, 404)


if __name__ == "__main__":
    unittest.main()
