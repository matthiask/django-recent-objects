from uuid import uuid4

from django.db import models


class Article(models.Model):
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField()


class Comment(models.Model):
    created_at = models.DateTimeField()
    comment = models.TextField()


class Payment(models.Model):
    identifier = models.UUIDField(default=uuid4, primary_key=True)
    created_at = models.DateTimeField()
