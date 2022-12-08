=====================
django-recent-objects
=====================

Recent objects fetching utilities

Usage:

.. code-block:: python

    from testapp.models import Article, Comment, Payment

    from recent_objects.recent_objects import RecentObjects

    ro = RecentObjects(
        [
            {
                "queryset": Article.objects.all(),
                "date_field": "created_at",
                # "type": "testapp.article",
            },
            {
                "queryset": Comment.objects.all(),
                "date_field": "created_at",
                # "type": "testapp.comment",
            },
            {
                "queryset": Payment.objects.all(),
                "date_field": "created_at",
                # "type": "testapp.payment",
            },
        ]
    )

    recent_10_objects = ro.page(paginate_by=10, page=1)

``recent_10_objects`` will now be a list of up to 10 dictionaries of the form:

.. code-block:: python

    [
      {
          "type": "testapp.article",
          "date": datetime(...),
          "pk": 24,
          "object": Article(),
      },
      {
          "type": "testapp.comment",
          "date": datetime(...),
          "pk": 42,
          "object": Comment(),
      },
      ...
    ]

You can optionally specify the ``type`` yourself in the recent objects spec
above. This may be useful when you want more control over the value or if
you're assembling several querysets using the same underlying model.
