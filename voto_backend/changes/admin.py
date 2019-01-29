from django.contrib import admin
from . import models


admin.site.register(models.Change)
admin.site.register(models.ChangeGroup)
