from config.admin import register_models

register_models(app_label='changes', models={
    'Change': ['default'],
    'ChangeGroup': ['default'],
})
