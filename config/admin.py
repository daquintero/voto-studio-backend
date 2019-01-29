from django.contrib import admin
from django.conf import settings


class MultiDBModelAdmin(admin.ModelAdmin):
    using = settings.MAIN_SITE_DB

    def save_model(self, request, obj, form, change):
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        obj.delete(using=self.using)

    def get_queryset(self, request):
        return super().get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return super().formfield_for_foreignkey(db_field, request, using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        return super().formfield_for_manytomany(db_field, request, using=self.using, **kwargs)


class MainSiteAdmin(admin.AdminSite):
    site_header = 'VotoInformado 2019 Admin'


main_site_admin = MainSiteAdmin(name='main_site_admin')
