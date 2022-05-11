from django.test import TestCase

from recent_objects.recent_objects import RecentObjects

from testapp.models import Article, Comment, Payment


ro = RecentObjects(
    [
        {
            "type": "article",
            "queryset": Article.objects.all(),
            "date_field": "created_at",
        },
        {
            "type": "comment",
            "queryset": Comment.objects.all(),
            "date_field": "created_at",
        },
        {
            "type": "payment",
            "queryset": Payment.objects.all(),
            "date_field": "created_at",
        },
    ]
)

class RecentObjectsTest(TestCase):
    def test_query(self):
        self.assertEqual(ro.page(paginate_by=10, page=1), [])
