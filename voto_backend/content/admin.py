from django.contrib import admin
from config.admin import main_site_admin, MultiDBModelAdmin
from . import models


admin.site.register(models.TwitterFeed)
admin.site.register(models.Image)
admin.site.register(models.Logo)
admin.site.register(models.Video)
admin.site.register(models.IconData)


class TwitterFeedAdmin(MultiDBModelAdmin):
    model = models.TwitterFeed


main_site_admin.register(models.TwitterFeed, TwitterFeedAdmin)
