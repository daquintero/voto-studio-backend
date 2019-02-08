from config.admin import register_models

register_models(app_label='spatial', models={
    'GeometryCollection': ['spatial'],
    'Geometry': ['spatial'],
    'DataSet': ['spatial'],
})
