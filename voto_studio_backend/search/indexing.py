import re

from django.apps import apps
from django.conf import settings
from django.core.exceptions import FieldError
from elasticsearch.helpers import bulk
from elasticsearch_dsl import Document, Text, Date, Boolean, Integer, Long, Object, Nested
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
        http_auth=(auth[0], auth[1])
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


def check_index_exists(model_label, using=settings.STUDIO_DB):
    """
    Determine whether the index has already
    been created.
    """

    return client.indices.exists(build_index_name(model_label, using=using))


def create_document_class(model_label, using=settings.STUDIO_DB):
    """
    Dynamically create an index class for a model we want to enable search on.
    """
    fields = get_fields(model_label=model_label)
    attr_dict = {f.name: FIELD_MAP[f.get_internal_type()] for f in fields}
    document_class = type(model_label.split('.')[1], (Document,), attr_dict)
    index_class = type('Index', (object,), {'name': build_index_name(model_label, using=using)})
    setattr(document_class, 'Index', index_class)

    return document_class


def create_document_classes(using=settings.STUDIO_DB):
    """
    Bulk create index classes for every model we want to perform search on.
    """
    document_classes = {build_index_name(model_label, using=using): create_document_class(model_label, using=using)
                        for model_label in MODELS_TO_INDEX}

    return document_classes


def get_document_classes(using=settings.STUDIO_DB):
    document_classes = apps.get_app_config('search').document_classes[using]

    return document_classes


def get_document_class(model_label, using=settings.STUDIO_DB):
    document_classes = get_document_classes(using=using)

    return document_classes[build_index_name(model_label, using=using)]


def bulk_indexing(using=settings.STUDIO_DB):
    """
    Bulk index existing instances for each model.
    """
    if isinstance(using, str):
        using = [using]
    elif isinstance(using, list):
        pass
    else:
        raise ValueError("'using' must be either a string or a list.")

    for alias in using:
        for index_name, document_class in get_document_classes(using=alias).items():
            document_class.init(index=document_class.Index.name)

        for model_label in MODELS_TO_INDEX:
            if check_index_exists(model_label, using=alias):
                model_class = get_model(model_label=model_label)
                try:
                    instances = model_class.objects.using(alias).filter(tracked=True)
                except FieldError:
                    instances = model_class.objects.using(alias).all()
                bulk(
                    client=client,
                    actions=(instance.create_document() for instance in instances.iterator())
                )


def clear_indices(using=settings.STUDIO_DB, confirm=False):
    """
    Delete all current indexes
    """
    if isinstance(using, str):
        using = [using]
    elif isinstance(using, list):
        using = using
    else:
        raise ValueError("'using' must be either a string or a list.")

    for alias in using:
        if not (settings.TESTING or confirm):
            raise Exception('Attempt to clear default indices without confirmation!')

        for model_label in MODELS_TO_INDEX:
            # If the index exists delete it.
            if check_index_exists(model_label, using=alias) and model_label != settings.AUTH_USER_MODEL:
                client.indices.delete(build_index_name(model_label, using=alias))
