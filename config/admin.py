from django.apps import apps
from django.contrib import admin


class MultiDBModelAdmin(admin.ModelAdmin):
    using = None

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
    site_header = 'VotoInformado 2019 Main Site Admin'


class SpatialAdmin(admin.AdminSite):
    site_header = 'VotoInformado 2019 Spatial Data Admin'


main_site_admin = MainSiteAdmin(name='main_site_admin')
spatial_admin = SpatialAdmin(name='spatial_admin')


ADMIN_SITES = {
    'main_site': main_site_admin,
    'spatial': spatial_admin,
}


def register_models(app_label=None, models=None, default_admin='default'):
    for model_name, db_list in models.items():
            # Register on the default admin site.
            try:
                model = apps.get_model(app_label, model_name)
            except LookupError as e:
                raise(LookupError(f'You are trying to add a non-existent model to the admin!. {e}'))

            for db in db_list:
                if db == default_admin:
                    admin.site.register(model)
                else:
                    admin_class = type(model_name, (MultiDBModelAdmin, ), {
                        'using': db,
                        'model': model,
                    })
                    # Dynamically import each custom admin
                    # site and register the model to it.
                    ADMIN_SITES[db].register(model, admin_class)
