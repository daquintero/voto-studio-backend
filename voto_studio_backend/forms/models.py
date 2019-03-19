from django.utils.deconstruct import deconstructible


def _is_numeric(model_class, table_head):
    field_type = model_class._meta.get_field(table_head).get_internal_type()

    return (field_type == 'FloatField' or
            field_type == 'IntegerField' or
            field_type == 'PositiveIntegerField' or
            field_type == 'AutoField')


class InfoMixin:
    def _get_descriptor_value(self, descriptor):
        field = self._meta.model._meta.get_field(descriptor)
        if len(field.choices):
            ret = getattr(self, f'get_{field.name}_display')()
        else:
            ret = str(getattr(self, field.name))

        return ret

    def _get_user_info(self):
        if hasattr(self, 'user') and self.user is not None:
            return {
                'user_email': self.user.email,
                'user_id': self.user.id,
            }
        else:
            return {}

    def get_table_values(self):
        """
        Return some simple info for the tables in VotoStudio's workshop.
        """
        table_descriptors = getattr(self, 'table_descriptors', None)
        if not table_descriptors:
            raise AttributeError(f"Please add the 'table_descriptors' field to the model '{self._meta.label}'")

        return {
            'id': self.id,
            'descriptors': [{
                'name': d,
                'value': self._get_descriptor_value(d),
            } for d in table_descriptors],
            'app_label': self._meta.app_label,
            'model_name': self._meta.model_name,
            'model_label': self._meta.label,
            **self._get_user_info(),
        }

    def get_table_heads(self, verbose=False):
        if verbose:
            return [{
                'id': table_head,
                'numeric': _is_numeric(self, table_head),
                'disable_padding': False,
                'label': table_head.replace('_', ' ').title(),
            } for table_head in [*getattr(self, 'table_descriptors', [])]]
        else:
            return [*getattr(self, 'table_descriptors', [])]

    def get_detail_info(self):
        """
        Return more detailed info for the detail view in VotoStudio's workshop.
        """
        detail_descriptors = getattr(self, 'detail_descriptors', None)
        if not detail_descriptors:
            raise AttributeError(f"Please add the 'detail_descriptors' field to the model '{self._meta.label}'")

        detail_values = [{
            'name': d,
            'value': getattr(self, d),
            'type': 'basic',
        } for d in detail_descriptors['basic']]

        related_descriptors = detail_descriptors['related']
        for related_descriptor in related_descriptors:
            field_name = related_descriptor['field']
            field = self._meta.get_field(field_name)
            field_value = getattr(self, field_name)
            # If this field on the instance
            # has a value then check its type.
            if field:
                field_type = field.get_internal_type()
                value = None
                if field_type == 'ManyToManyField':
                    value = [[{
                        'name': attr,
                        'value': getattr(o, attr)
                    } for attr in ('id', *related_descriptor['attrs'])] for o in field_value.all()]

                if field_type == 'ForeignKey' or field_type == 'OneToOneField':
                    value = [{
                        'name': attr,
                        'value': getattr(field_value, attr, None),
                    } for attr in related_descriptor['attrs']]

                detail_values.append({
                    'name': field_name,
                    'model_label': field.related_model._meta.label,
                    'value': value,
                    'type': 'related',
                })

        return detail_values


class JSONBaseField:
    def __init__(self, read_only=False):
        self.read_only = read_only


class JSONAutoField(JSONBaseField):
    type = 'number'
    auto = True

    def __init__(self, *, read_only=True, unique=True):
        self.unique = unique
        super().__init__(read_only=read_only)


class JSONCharField(JSONBaseField):
    type = 'text'

    def __init__(self, max_length, *, read_only=False):
        self.max_length = max_length
        super().__init__(read_only=read_only)


class JSONChoiceField(JSONBaseField):
    type = 'select'

    def __init__(self, read_only=False, choices=None):
        self.choices = tuple((value, str(label)) for value, label in choices)
        super().__init__(read_only=read_only)


class JSONTextField(JSONBaseField):
    type = 'textarea'


@deconstructible
class JSONModel:
    def __call__(self, *args, **kwargs):
        return self._json

    def _get_attrs(self):
        attrs = []
        for attr, val in dict(vars(self.__class__)).items():
            if not attr.startswith('_'):
                attrs.append((attr, val))

        return attrs

    def _get_choices(self, field_class):
        options = []
        if hasattr(field_class, 'choices'):
            for value, label in field_class.choices:
                options.append({
                    'label': label,
                    'value': value,
                })
        return {
            'options': options,
        }

    @property
    def _json(self):
        json = {
            'schema': {
                'fields': [],
                'validation': [],
            },
            'sub_instances': [],
        }
        for field_name, field_class in self._get_attrs():
            json['schema']['fields'].append({
                'name': field_name,
                'type': field_class.type,
                'read_only': field_class.read_only,
                **self._get_choices(field_class),
            })

        return json
