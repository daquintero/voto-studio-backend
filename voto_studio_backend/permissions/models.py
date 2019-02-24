from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.shortcuts import get_object_or_404
from .core import Permission
from .exceptions import PermissionError
from voto_studio_backend.users.models import User


READ_OPERATION = 'read'
WRITE_OPERATION = 'write'
DELETE_OPERATION = 'delete'
RELATE_OPERATION = 'relate'
COMMIT_OPERATION = 'commit'
REVERT_OPERATION = 'revert'


class PermissionsBaseModel(models.Model):
    # By default only one user has CRUD permissions on a piece of
    # content. Users have the option to share share these permissions
    # with other users with varying levels of control.
    permitted_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='%(app_label)s_%(class)s_related',
    )
    permissions_dict = JSONField(blank=True, default=dict)

    class Meta:
        abstract = True

    def get_permission_level(self, user):
        return Permission(self.permissions_dict[str(user.id)])

    def set_permission_level(self, user, permission_level):
        if not isinstance(permission_level, str):
            raise TypeError(f"Argument 'permission_level' must be a str (not {type(permission_level)}).")

        permission_dict = self.permissions_dict
        permission_dict[str(user.id)] = str(Permission(permission_level))
        self.save(using=settings.STUDIO_DB)

        self.permitted_users.add(user)

        return Permission(permission_level)

    def revoke_user(self, user):
        if user in self.permitted_users.all():
            permissions_dict = self.permissions_dict
            permissions_dict[str(user.id)] = None
            self.save(using=settings.STUDIO_DB)

            self.permitted_users.remove(user)
        else:
            raise PermissionError(f"User {user} is not in 'permitted_users'.")

    def is_permitted(self, user, operation):
        if user.is_researcher:
            # if operation == COMMIT_OPERATION:
            return True
            # migration_bot = get_object_or_404(User, email='migration@bot.com')
            # if self.user == migration_bot:
            #     return True
        if user == self.user and not operation == COMMIT_OPERATION:
            return True
        if user in self.permitted_users.all():
            return Permission(operation) <= self.get_permission_level(user)
        return False

    def can_read(self, user):
        return self.is_permitted(user, READ_OPERATION)

    def can_write(self, user):
        return self.is_permitted(user, WRITE_OPERATION)

    def can_delete(self, user):
        return self.is_permitted(user, DELETE_OPERATION)

    def can_relate(self, user):
        return self.is_permitted(user, RELATE_OPERATION)

    def can_revert(self, user):
        return self.is_permitted(user, REVERT_OPERATION)

    def can_commit(self, user):
        return self.is_permitted(user, COMMIT_OPERATION)
