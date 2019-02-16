from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models


READ_OPERATION = 'read'
WRITE_OPERATION = 'write'
DELETE_OPERATION = 'delete'
RELATE_OPERATION = 'relate'
COMMIT_OPERATION = 'commit'
REVERT_OPERATION = 'revert'
ADMIN_OPERATIONS = [
    READ_OPERATION,
    WRITE_OPERATION,
    DELETE_OPERATION,
    RELATE_OPERATION,
    COMMIT_OPERATION,
    REVERT_OPERATION,
]


class PermissionError(Exception):
    pass


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

    def permit_user(self, user, operations):
        if not isinstance(operations, (str, list,)):
            raise TypeError(f"Argument 'operations' must be a str or list (not {type(operations)}).")
        operations = [operations] if isinstance(operations, str) else operations

        self.permitted_users.add(user)
        permission_dict = self.permissions_dict

        if user.id not in permission_dict.keys():
            permission_dict[user.id] = []
        operations = list(set(permission_dict[user.id] + operations))
        permission_dict[user.id] = operations
        self.save(using=settings.STUDIO_DB)

        return operations

    def set_admin(self, user):
        self.permit_user(user, ADMIN_OPERATIONS)

    def revoke_user(self, user, operations=None, admin=None):
        if not isinstance(operations, (str, list,)):
            raise TypeError(f"Argument 'operations' must be a str or list (not {type(operations)}).")
        operations = [operations] if isinstance(operations, str) else operations

        if user in self.permitted_users.all():
            # A python tuple is converted to a list when dumped
            # to json so we don't need to user ``list()``.
            permission_list = self.permissions_dict[user.id]
            for operation in (operations if not admin else ADMIN_OPERATIONS):
                try:
                    permission_list.remove(operation)
                except ValueError as e:
                    raise ValueError(f"Operation {operation} is not a valid permission or this "
                                     f"user did not have this permission. {e}")

            if not len(permission_list):
                self.permitted_users.remove(user)

            self.permissions_dict[user.id] = permission_list
            self.save(using=settings.STUDIO_DB)

            return permission_list

        raise PermissionError(f"User {user} is not in 'permitted_users'.")

    def is_permitted(self, user, operation):
        if user == self.user:
            return True
        if user in self.permitted_users.all():
            return operation in self.permissions_dict[user.id]

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

    def is_admin(self, user):
        if user in self.permitted_users.all():
            return self.permissions_dict[user.id] == ADMIN_OPERATIONS
        return False
