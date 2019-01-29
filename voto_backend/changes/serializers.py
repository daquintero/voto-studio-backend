from rest_framework import serializers
from . import models


class UserEmailMixin(serializers.ModelSerializer):
    class Meta:
        abstract = True

    user_email = serializers.SerializerMethodField()

    def get_user_email(self, obj):
        return obj.user.email


class ChangeListSerializer(UserEmailMixin):
    class Meta:
        model = models.Change
        fields = (
            'id',
            'name',
            'date_created',
            'committed',
            'reverted',
            'user_email',
        )


class CommittedChangeListSerializer(UserEmailMixin):
    class Meta:
        model = models.Change
        fields = (
            'id',
            'name',
            'date_committed',
            'user_email',
        )


class ChangeGroupSerializer(UserEmailMixin):
    changes_committed_count = serializers.SerializerMethodField()

    class Meta:
        model = models.ChangeGroup
        fields = (
            'id',
            'description',
            'date_created',
            'changes_committed_count',
            'user_email',
        )

    def get_changes_committed_count(self, obj):
        return obj.changes_committed.count()
