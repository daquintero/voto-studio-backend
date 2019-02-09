from django.conf import settings
from django.db import models
from elasticsearch.exceptions import NotFoundError, RequestError
from elasticsearch_dsl import Search, Q
from .utils import get_fields
from .indexing import build_index_name, get_document_class


def _get_search_type(terms):
    return 'terms' if isinstance(terms, list) else 'match'


class IndexingManager(models.Manager):
    def get_query(self, using=settings.STUDIO_DB, sort=None, **kwargs):
        search = Search(index=build_index_name(self.model._meta.label, using=using))

        must = [Q(_get_search_type(k[1]), **{k[0]: k[1]}) for k in kwargs.get('must', {}).items()]
        must_not = [Q(_get_search_type(k[1]), **{k[0]: k[1]}) for k in kwargs.get('must_not', {}).items()]

        query = search.query(Q(({'bool': {'must': must, 'must_not': must_not}})))

        if sort and self.model.objects.using(using).count():
            query = query.sort(sort)

        return query

    def filter(self, using=settings.STUDIO_DB, page=0, size=10, verbose=False, sort=None, search=None, **kwargs):
        query = self.get_query(using=using, sort=sort, **kwargs)

        size = int(size)
        page = int(page)
        from_ = page * size
        to = from_ + size

        if search and len(search):
            executed_search = query.query('query_string', query=search)[from_:to].execute()
        else:
            executed_search = query[from_:to].execute()

        if verbose:
            response = executed_search.to_dict()
        else:
            response = [hit.to_dict() for hit in executed_search.hits]

        return response


class IndexingMixin:
    """
    Mixin that adds methods allowing a model
    to be indexed by Elasticsearch.
    """
    def get_kwargs(self, model_label):
        from voto_backend.forms.views import parse_value

        fields = get_fields(model_label)
        return {f.name: parse_value(f, getattr(self, f.name)) for f in fields}

    def create_document(self, using=settings.STUDIO_DB):
        model_label = self._meta.label
        obj = get_document_class(model_label, using=using)(
            meta={'id': self.id},
            model_label=model_label,
            user=getattr(getattr(self, 'user', None), 'id', None),
            table_values=self.get_table_values(),
            **self.get_kwargs(model_label),
            refresh=True,
        )
        obj.save(index=build_index_name(model_label, using=using))

        return obj.to_dict(include_meta=True)

    def update_document(self, using=settings.STUDIO_DB):
        model_label = self._meta.label
        document_class = get_document_class(model_label, using=using)
        document = document_class.get(id=self.id, index=build_index_name(model_label, using=using))
        document.update(
            table_values=self.get_table_values(),
            refresh=True,
        )

        return document

    def delete_document(self, using=settings.STUDIO_DB):
        try:
            query = self._meta.model.search.get_query(must={'id': self.id}, using=using)
            query.delete()
        except NotFoundError as e:
            pass
