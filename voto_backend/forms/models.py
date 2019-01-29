class InfoMixin:
    @property
    def table_values(self):
        """
        Return some simple info for the tables in VotoStudio's workshop.
        """
        table_descriptors = getattr(self, 'table_descriptors', None)
        if not table_descriptors:
            raise AttributeError(f"Please add the 'table_descriptors' field to the model '{self._meta.label}'")

        return {
            'id': self.id,
            'descriptors': {
                'values': [{
                    'name': d,
                    'value': str(getattr(self, d)),
                } for d in table_descriptors]},
            'user_email': self.user.email if self.user else None,
            'app_label': self._meta.app_label,
            'model_name': self._meta.model_name,
            'model_label': self._meta.label,
        }

    @property
    def table_heads(self):
        return [*getattr(self, 'table_descriptors', None)]

    @property
    def detail_info(self):
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
