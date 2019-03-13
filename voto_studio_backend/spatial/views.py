import json

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry, GeometryCollection, MultiPolygon, Polygon
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


def recur(geometry):

    return


def create_circuitos():
    geometries = models.DataSet.objects.using(settings.SPATIAL_DB).get(location_id_name='CIRCUITO').geometries

    gid_list = []
    for geometry in geometries.all():
        properties = geometry.properties
        gid_list.append(properties['CIRCUITO'])

    print(len(gid_list))
    gid_list = list(set(gid_list))

    outer_json = {
        'type': 'FeatureCollection',
        'features': [],
    }
    geometry_collections = []
    total_geoms = 0
    for gid in gid_list:
        geometries_in_gid = geometries.filter(properties__CIRCUITO=gid)
        total_geoms += len(geometries_in_gid)

        if (len(geometries_in_gid) > 1):
            for geometry in geometries_in_gid:
                geometry = geometry.geometry
                new_geometry = new_geometry.union(geometry)

            # print(json.loads(geometry_collection.geojson)['geometries'][0])

            inner_json = {
                'type': 'Feature',
                'geometry': json.loads(geometry_collection.geojson)['geometries'][1],
                'properties': {
                    'CIRCUITO': gid,
                },
            }
        else:
            inner_json = {
                'type': 'Feature',
                'geometry': json.loads(geometries_in_gid[0].geojson)['geometry'],
                'properties': {
                    'CIRCUITO': gid
                },
            }

        outer_json['features'].append(inner_json)

    with open('./voto_studio_backend/spatial/data/circuito.json', 'w') as outfile:
        json.dump(outer_json, outfile)

    print(total_geoms)
    return outer_json, geometry_collections, geometries_in_gid


def test():
    geometries = models.DataSet.objects.using(settings.SPATIAL_DB).get(location_id_name='CIRCUITO').geometries

    gid_list = []
    for geometry in geometries.all():
        properties = geometry.properties
        gid_list.append(properties['CIRCUITO'])
    gid_list = list(set(gid_list))

    outer_json = {
        'type': 'FeatureCollection',
        'features': [],
    }

    geometry_unions = []
    for index, gid in enumerate(gid_list):
        try:
            print(index)
            geometries_in_gid = geometries.filter(properties__CIRCUITO=gid)
            geometries_in_gid = [g.geometry for g in geometries_in_gid]
            print(geometries_in_gid, gid)
            geometry_union = geometries_in_gid[0]
            geometries_in_gid = geometries_in_gid[1:]

            for geometry in geometries_in_gid:
                geometry_union = geometry_union.union(geometry)
            geometry_unions.append(geometry_union)

            inner_json = {
                'type': 'Feature',
                'geometry': json.loads(geometry_union.json),
                'properties': {
                    'CIRCUITO': gid,
                },
            }
            outer_json['features'].append(inner_json)
        except:
            print('passing', geometries_in_gid, gid)

    with open('./voto_studio_backend/spatial/data/circuito.json', 'w') as outfile:
        json.dump(outer_json, outfile)


def test2():
    geometries = models.DataSet.objects.using(settings.SPATIAL_DB).get(location_id_name='CIRCUITO').geometries

    gid_list = []
    for geometry in geometries.all():
        properties = geometry.properties
        gid_list.append(properties['CIRCUITO'])
    gid_list = list(set(gid_list))

    outer_json = {
        'type': 'FeatureCollection',
        'features': [],
    }

    geometry_unions = []
    for index, gid in enumerate(gid_list):
        print(index)
        geometries_in_gid = geometries.filter(properties__CIRCUITO=gid)
        geometries_in_gid = [g.geometry for g in geometries_in_gid]

        mp = MultiPolygon(tuple(MultiPolygon(g) for g in geometries_in_gid))

        inner_json = {
            'type': 'Feature',
            'geometry': json.loads(mp.json),
            'properties': {
                'CIRCUITO': gid,
            },
        }
        outer_json['features'].append(inner_json)

    with open('./voto_studio_backend/spatial/data/circuito.json', 'w') as outfile:
        json.dump(outer_json, outfile)
