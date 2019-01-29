from django.contrib import admin
from config.admin import main_site_admin, MultiDBModelAdmin
from . import models


admin.site.register(models.User)
admin.site.register(models.Researcher)


class UserAdmin(MultiDBModelAdmin):
    model = models.User


main_site_admin.register(models.User, UserAdmin)
