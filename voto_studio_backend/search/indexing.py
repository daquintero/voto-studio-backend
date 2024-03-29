import re
from itertools import permutations

from django.apps import apps
from django.conf import settings
from django.core.exceptions import FieldError
from elasticsearch.helpers import bulk
from elasticsearch_dsl import (
    Document, Index, Text, Date, Boolean, Integer, Long, Nested, Completion, analyzer, token_filter, Keyword,
)
from elasticsearch_dsl.connections import create_connection

from shared.utils import get_model
from .utils import get_models_to_index, get_fields


bonsai = settings.BONSAI_URL
client = None
if bonsai:
    auth = re.search('https\:\/\/(.*)\@', bonsai).group(1).split(':')
    host = bonsai.replace('https://%s:%s@' % (auth[0], auth[1]), '')
    client = create_connection(
        host=host,
        port=443,
        use_ssl=True,
        http_auth=(auth[0], auth[1]),
        timeout=30,
    )
else:
    client = create_connection()


FIELD_MAP = {
    'AutoField': Integer,
    'CharField': Text,
    'TextField': Text,
    'URLField': Text,
    'IntegerField': Integer,
    'PositiveIntegerField': Integer,
    'FloatField': Long,
    'DateField': Date,
    'DateTimeField': Date,
    'BooleanField': Boolean,
    'FileField': None,
    'JSONField': Nested,
}


MODELS_TO_INDEX = get_models_to_index()


def build_index_name(model_label, is_class=False, using=settings.STUDIO_DB):
    if is_class:
        return f'{model_label.split(".")[1]}Index{using.capitalize()}' + ('Test' if settings.TESTING else '')
    else:
        return f'{model_label.split(".")[1].lower()}-{using.lower()}' + ('-test' if settings.TESTING else '')


def get_index_name(index_name=None, model_label=None, using=settings.STUDIO_DB):
    if index_name is not None:
        return index_name
    if model_label is not None:
        return build_index_name(model_label, using=using)


def check_index_exists(index_name=None, model_label=None, using=settings.STUDIO_DB):
    """
    Determine whether the index has already
    been created.
    """
    return client.indices.exists(get_index_name(
        index_name=index_name,
        model_label=model_label,
        using=using
    ))


ascii_fold = analyzer(
    'ascii_fold',
    tokenizer='whitespace',
    filter=[
        'lowercase',
        token_filter('ascii_fold', 'asciifolding'),
    ],
)


def clean(self):
    """
    Automatically construct the suggestion input and weight by taking all
    possible permutation of the instance's ``search_autocomplete_field``
    as ``input`` and taking 1 as ``weight`` (TODO: Improve weighting).
    """
    model_class = get_model(self.model_label)
    field_value = getattr(self, model_class.search_autocomplete_field, '')
    if field_value is not None:
        self.suggest = {
            'input': [field_value],
            'weight': 1,
        }
    else:
        self.suggest = {
            'input': [],
            'weight': 0,
        }


def get_field(model_label, field):
    model_class = get_model(model_label=model_label)
    field_type = field.get_internal_type()

    field_kwargs = {}
    if field.name in getattr(model_class, 'search_boost_fields', ()):
        field_kwargs.update({
            'boost': 10,
        })
    if field.name in getattr(model_class, 'search_keyword_fields', ()):
        field_kwargs.update({
            'fields': {
                'raw': Keyword(),
            },
        })

    return FIELD_MAP[field_type](**field_kwargs)


def create_document_class(model_label, using=settings.STUDIO_DB):
    """
    Dynamically create an index class for a model we want to enable search on.
    """
    excluded_fields = (
        'password',
        'permissions_dict',
        'order',
    )

    fields = [field for field in get_fields(model_label=model_label) if field.name not in excluded_fields]
    attr_dict = {
        field.name: get_field(model_label, field) for field in fields
    }
    attr_dict.update({
        'model_label': model_label,
        'clean': clean,
        'suggest': Completion(analyzer=ascii_fold),
    })
    document_class = type(model_label.split('.')[1], (Document,), attr_dict)
    index_class = type('Index', (object,), {'name': build_index_name(model_label, using=using)})
    setattr(document_class, 'Index', index_class)

    return document_class


def create_document_classes(using=settings.STUDIO_DB):
    """
    Bulk create index classes for every model we want to perform search on.
    """
    document_classes = {
        build_index_name(model_label, using=using): create_document_class(model_label, using=using)
        for model_label in MODELS_TO_INDEX
    }

    return document_classes


def get_document_classes(using=settings.STUDIO_DB):
    document_classes = apps.get_app_config('search').document_classes[using]

    return document_classes


def get_document_class(model_label, using=settings.STUDIO_DB):
    document_classes = get_document_classes(using=using)

    return document_classes[build_index_name(model_label, using=using)]


def create_base_index(index_name=None, model_label=None, using=settings.STUDIO_DB):
    index = Index(get_index_name(index_name=index_name, model_label=model_label, using=using))
    index.settings(
        number_of_shards=settings.NUMBER_OF_SHARDS,
        number_of_replicas=settings.NUMBER_OF_REPLICAS,
    )

    return index


def indexing(model_label, using=settings.STUDIO_DB):
    """
    Index existing instances for each model.
    """
    if check_index_exists(model_label, using=using):
        model_class = get_model(model_label=model_label)
        try:
            instances = model_class.objects.using(using).filter(tracked=True)
        except FieldError:
            instances = model_class.objects.using(using).all()
        bulk(
            client=client,
            actions=(instance.create_document(using=using) for instance in instances.iterator())
        )


def _parse_using(using):
    if isinstance(using, str):
        using = [using]
    elif isinstance(using, list):
        pass
    else:
        raise ValueError("'using' must be either a string or a list.")

    return using


def bulk_indexing(using=settings.STUDIO_DB):
    """
    Bulk index existing instances for each model.
    """
    using = _parse_using(using)
    for alias in using:
        for index_name, document_class in get_document_classes(using=alias).items():
            if not check_index_exists(index_name=index_name, using=alias):
                index = create_base_index(index_name=index_name)
                index.document(document_class)
                index.create()

        for model_label in MODELS_TO_INDEX:
            model_class = get_model(model_label=model_label)
            try:
                instances = model_class.objects.using(alias).filter(tracked=True)
            except FieldError:
                instances = model_class.objects.using(alias).all()
            bulk(
                client=client,
                actions=(instance.create_document(using=alias) for instance in instances.iterator())
            )


def clear_indices(using=settings.STUDIO_DB, confirm=False):
    """
    Delete all current indexes
    """
    using = _parse_using(using)
    for alias in using:
        if not (settings.TESTING or confirm):
            raise Exception('Attempt to clear default indices without confirmation!')

        for model_label in MODELS_TO_INDEX:
            # If the index exists delete it.
            if check_index_exists(model_label=model_label, using=alias) and not \
               model_label == settings.AUTH_USER_MODEL:
                client.indices.delete(build_index_name(model_label, using=alias))
