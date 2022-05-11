import datetime as dt

from django.test import TestCase
from django.utils.timezone import now
from testapp.models import Article, Comment, Payment

from recent_objects.recent_objects import RecentObjects


class RecentObjectsTest(TestCase):
    def test_query(self):
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

        with self.assertNumQueries(1):
            self.assertEqual(ro.page(paginate_by=10, page=1), [])

        a = Article.objects.create(created_at=now() - dt.timedelta(seconds=300))
        c = Comment.objects.create(created_at=now() - dt.timedelta(seconds=200))
        p = Payment.objects.create(created_at=now() - dt.timedelta(seconds=100))
        a2 = Article.objects.create(created_at=now() - dt.timedelta(seconds=0))

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

    def test_filter(self):
        a = Article.objects.create(created_at=now() - dt.timedelta(seconds=300))
        c = Comment.objects.create(created_at=now() - dt.timedelta(seconds=200))
        p = Payment.objects.create(created_at=now() - dt.timedelta(seconds=100))
        Article.objects.create(created_at=now() - dt.timedelta(seconds=0))

        cutoff = now() - dt.timedelta(seconds=50)
        ro = RecentObjects(
            [
                {
                    "queryset": Article.objects.filter(created_at__lte=cutoff),
                    "date_field": "created_at",
                },
                {
                    "queryset": Comment.objects.filter(created_at__lte=cutoff),
                    "date_field": "created_at",
                },
                {
                    "queryset": Payment.objects.filter(created_at__lte=cutoff),
                    "date_field": "created_at",
                },
            ]
        )

        self.assertEqual(
            [obj["object"] for obj in ro.materialize(ro.union())],
            [p, c, a],
        )
        self.assertEqual(
            [obj["object"] for obj in ro.materialize(ro.union()[:2])],
            [p, c],
        )
