import json

from django.conf import settings
from django.contrib.gis.geos import GeometryCollection
from . import models
from voto_studio_backend.political.models import Individual
from voto_studio_backend.changes.models import Change


def create_individual_loop():
    geometries = models.DataSet.objects.using(settings.SPATIAL_DB).get(location_id_name='CIRCUITO').geometries
    individuals = Individual.objects.using(settings.MAIN_SITE_DB).filter(tracked=True)

    ret = []
    for individual in individuals:
        geometry_tuple = tuple(g.geometry for g in geometries.filter(location_id=individual.location_id))
        geometry_collection = GeometryCollection(geometry_tuple)
        ret.append({
            'id': individual.id,
            'name': individual.name,
            'brief_description': individual.brief_description,
            'statistics': individual.statistics,
            'location_id': individual.location_id,
            'centroid': tuple(geometry_collection.centroid.coord_seq),
        })

    with open('./voto_studio_backend/spatial/data/individuals-map-loop.json', 'w') as outfile:
        json.dump(ret, outfile)

    return ret


def create_centroid_list():
    geometries = models.DataSet.objects.using(settings.SPATIAL_DB).get(location_id_name='CIRCUITO').geometries

    centroid_list = []
    for geometry_instance in geometries.all():
        centroid_list.append({
            'coordinates': geometry_instance.geometry.centroid.coords,
        })

    with open('./voto_studio_backend/spatial/data/hex.json', 'w') as outfile:
        json.dump(centroid_list, outfile)

    return json.dumps(centroid_list)
