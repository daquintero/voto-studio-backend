from config.admin import register_models

register_models(app_label='users', models={
    'User': ['default', 'main_site'],
    'Researcher': ['default', 'main_site'],
})
