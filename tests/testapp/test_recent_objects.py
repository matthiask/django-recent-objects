from django.test import TestCase
from django.utils.timezone import now
from testapp.models import Article, Comment, Payment

from recent_objects.recent_objects import RecentObjects


ro = RecentObjects(
    [
        {
            "type": "article",
            "queryset": Article.objects.all(),
            "date_field": "created_at",
        },
        {
            "queryset": Comment.objects.all(),
            "date_field": "created_at",
        },
        {
            "queryset": Payment.objects.all(),
            "date_field": "created_at",
        },
    ]
)


class RecentObjectsTest(TestCase):
    def test_query(self):
        with self.assertNumQueries(1):
            self.assertEqual(ro.page(paginate_by=10, page=1), [])

        a = Article.objects.create(created_at=now())
        c = Comment.objects.create(created_at=now())
        p = Payment.objects.create(created_at=now())
        a2 = Article.objects.create(created_at=now())

        with self.assertNumQueries(4):
            # 1 * count + 1 * union + 2 * materialize
            first_page = ro.page(paginate_by=2, page=1)
        with self.assertNumQueries(4):
            # 1 * count + 1 * union + 1 * materialize
            second_page = ro.page(paginate_by=2, page=2)

        self.assertEqual(
            [obj["object"] for obj in first_page],
            [a2, p],
        )
        self.assertEqual(
            [obj["object"] for obj in second_page],
            [c, a],
        )

        with self.assertNumQueries(5):
            # 1 * count + 1 * union + 3 * materialize
            self.assertEqual(
                ro.page(paginate_by=99, page=1),
                [
                    {
                        "type": "article",
                        "date": a2.created_at,
                        "pk": a2.pk,
                        "object": a2,
                    },
                    {
                        "type": "testapp.payment",
                        "date": p.created_at,
                        "pk": p.pk,
                        "object": p,
                    },
                    {
                        "type": "testapp.comment",
                        "date": c.created_at,
                        "pk": c.pk,
                        "object": c,
                    },
                    {
                        "type": "article",
                        "date": a.created_at,
                        "pk": a.pk,
                        "object": a,
                    },
                ],
            )
