from config.admin import register_models

register_models(app_label='media', models={
    'Image': ['default', 'main_site'],
    'Video': ['default', 'main_site'],
    'Resource': ['default', 'main_site'],
})
