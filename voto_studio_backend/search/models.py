from django.conf import settings
from django.db import models
from elasticsearch.exceptions import NotFoundError
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
    def get_kwargs(self):
        from voto_studio_backend.forms.views import parse_value

        excluded_fields = (
            'password',
            'permissions_dict',
            'order',
        )

        fields = [field for field in get_fields(model_class=self) if field.name not in excluded_fields]
        ret = {}
        for field in fields:
            if field.get_internal_type() == 'JSONField':
                ret.update({field.name: getattr(self, field.name)})
            else:
                if len(field.choices):
                    ret.update({field.name: getattr(self, f'get_{field.name}_display')()})
                else:
                    ret.update({field.name: parse_value(field, getattr(self, field.name))})

        if hasattr(self, 'search_method_fields'):
            for method_field_name in self.search_method_fields:
                ret.update({
                    method_field_name: getattr(self, f'get_{method_field_name}')()
                })

        return ret

    def get_media(self):
        from voto_studio_backend.media.views import FIELD_SERIALIZER_MAP

        ret = {}
        for field_name, id_list in self.order.items():
            media_model_class = getattr(self, field_name).model
            media_instances = media_model_class.objects.filter(id__in=id_list)
            ret.update({field_name: FIELD_SERIALIZER_MAP[field_name](media_instances, many=True).data})

        return ret

    def get_user(self):
        user = getattr(self, 'user', None)
        if user is not None:
            return user.id
        return None

    def create_document(self, using=settings.STUDIO_DB):
        model_label = self._meta.label
        obj = get_document_class(model_label, using=using)(
            meta={'id': self.id},
            model_label=model_label,
            size='full',
            user=self.get_user(),
            media=self.get_media(),
            **self.get_kwargs(),
        )
        obj.save(index=build_index_name(model_label=model_label, using=using))

        return obj.to_dict(include_meta=True)

    def update_document(self, using=settings.STUDIO_DB):
        model_label = self._meta.label
        document_class = get_document_class(model_label, using=using)
        document = document_class.get(id=self.id, index=build_index_name(model_label=model_label, using=using))
        document.update(
            user=self.get_user(),
            media=self.get_media(),
            **self.get_kwargs(),
        )

        return document

    def delete_document(self, using=settings.STUDIO_DB):
        try:
            query = self._meta.model.search.get_query(must={'id': self.id}, using=using)
            query.delete()
        except NotFoundError:
            pass
