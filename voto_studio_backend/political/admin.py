from config.admin import register_models

register_models('political', models={
    'Law': ['default', 'main_site'],
    'Individual': ['default', 'main_site'],
    'Campaign': ['default', 'main_site'],
    'Organization': ['default', 'main_site'],
    'Promise': ['default', 'main_site'],
    'Achievement': ['default', 'main_site'],
    'Controversy': ['default', 'main_site'],
})
