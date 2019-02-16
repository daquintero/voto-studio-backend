from rest_framework import serializers


class GeneralListSerializer(serializers.ModelSerializer):
    def __init__(self, *args, model_class=None, **kwargs):
        self.Meta.model = model_class
        super().__init__(*args, **kwargs)

    table_values = serializers.ReadOnlyField(source='get_table_values')

    class Meta:
        model = None
        fields = (
            'id',
            'table_values',
        )


class GeneralSerializer(serializers.ModelSerializer):
    def __init__(self, *args, model_class=None, **kwargs):
        self.Meta.model = model_class
        super().__init__(*args, **kwargs)

    table_values = serializers.SerializerMethodField(source='get_table_values')

    class Meta:
        model = None
        fields = '__all__'


class GeneralDetailSerializer(serializers.ModelSerializer):
    def __init__(self, *args, model_class=None, **kwargs):
        self.Meta.model = model_class
        super().__init__(*args, **kwargs)

    detail_info = serializers.ReadOnlyField(source='get_detail_info')
    model_label = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id',
            'detail_info',
            'model_label'
        )

    def get_model_label(self, obj):
        return self.Meta.model._meta.label
