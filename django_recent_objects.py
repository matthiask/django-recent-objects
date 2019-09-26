from collections import defaultdict

from django.core.paginator import Paginator
from django.db.models import F, Value, CharField
from django.db.models.functions import Cast


class RecentObjects(object):
    # Inspired by https://gist.github.com/simonw/dd0da256716c0b0ec4efe12a81caec45

    def __init__(self, querysets_spec):
        self._querysets_spec = querysets_spec
        for spec in self._querysets_spec:
            spec["pk"] = spec["queryset"].model._meta.pk
        self._by_type = {spec["type"]: spec for spec in self._querysets_spec}

    def union(self):
        id_querysets = [
            spec["queryset"]
            .annotate(
                __ro_date=F(spec["date_field"]),
                __ro_type=Value(spec["type"], output_field=CharField()),
                __ro_pk=Cast(F(spec["pk"].name), output_field=CharField()),
            )
            .values("__ro_pk", "__ro_date", "__ro_type")
            for spec in self._querysets_spec
        ]
        return id_querysets[0].union(*id_querysets[1:]).order_by("-__ro_date")

    def materialize(self, id_queryset):
        id_map = defaultdict(set)
        for row in id_queryset:
            row["pk"] = self._by_type[row["__ro_type"]]["pk"].to_python(row["__ro_pk"])
            id_map[row["__ro_type"]].add(row["pk"])

        objects = {
            spec["type"]: {
                instance.pk: instance
                for instance in spec["queryset"].filter(pk__in=id_map[spec["type"]])
            }
            for spec in self._querysets_spec
            if id_map.get(spec["type"])
        }

        return [
            {
                "type": row["__ro_type"],
                "date": row["__ro_date"],
                "object": objects[row["__ro_type"]][row["pk"]],
            }
            for row in id_queryset
        ]

    def page(self, *, paginate_by, page=None):
        return self.materialize(Paginator(self.union(), paginate_by).get_page(page))
