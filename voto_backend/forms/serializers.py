from rest_framework import serializers


class GeneralListSerializer(serializers.ModelSerializer):
    def __init__(self, *args, model_class=None, **kwargs):
        self.Meta.model = model_class
        super().__init__(*args, **kwargs)

    table_values = serializers.SerializerMethodField()

    class Meta:
        model = None
        fields = (
            'id',
            'table_values',
        )

    def get_table_values(self, obj):
        return obj.table_values


class GeneralSerializer(serializers.ModelSerializer):
    def __init__(self, *args, model_class=None, **kwargs):
        self.Meta.model = model_class
        super().__init__(*args, **kwargs)

    table_values = serializers.SerializerMethodField()

    class Meta:
        model = None
        fields = '__all__'

    def get_table_values(self, obj):
        return obj.table_values


class GeneralDetailSerializer(serializers.ModelSerializer):
    def __init__(self, *args, model_class=None, **kwargs):
        self.Meta.model = model_class
        super().__init__(*args, **kwargs)

    detail_values = serializers.SerializerMethodField()
    model_label = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id',
            'detail_values',
            'model_label'
        )

    def get_detail_values(self, obj):
        return obj.detail_info

    def get_model_label(self, obj):
        return self.Meta.model._meta.label
