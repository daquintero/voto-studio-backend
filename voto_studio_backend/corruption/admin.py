from config.admin import register_models

register_models(app_label='corruption', models={
    'InformativeSnippet': ['default', 'main_site'],
    'CorruptionCase': ['default', 'main_site'],
    'FinancialItem': ['default', 'main_site'],
})
