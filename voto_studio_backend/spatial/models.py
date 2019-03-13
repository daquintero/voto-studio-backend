import json

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry, GeometryCollection as GEOSGeometryCollection
from django.contrib.postgres.fields import JSONField


class GeometryCollectionManager(models.Manager):
    def create_from_json(self, name=None, file=None, location_id_name=None):
        if file is None or not file.name.endswith(('.geojson', '.json')):
            raise ValueError('Provide a json or geojson file.')

        geometry_collection = self.model(
            name=name,
            geometry_collection=GEOSGeometryCollection(
                tuple(GEOSGeometry(g.geometry) for g in Geometry.objects.create_from_json(
                    file=file,
                    location_id_name=location_id_name,
                )))
        )
        geometry_collection.save(using=settings.SPATIAL_DB)

        return geometry_collection


class GeometryCollection(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)
    geometry_collection = models.GeometryCollectionField(blank=True, null=True)
    properties = JSONField(default=dict)

    objects = GeometryCollectionManager()


class GeometryManager(models.Manager):
    def create_from_json(self, name=None, file=None, location_id_name=None, **kwargs):
        if file is None or not file.name.endswith(('.geojson', '.json')):
            raise ValueError('Provide a json or geojson file.')

        data = json.loads(file.read())
        features = data['features']

        ret = []
        for feature in features:
            properties = feature['properties']
            location_id = properties[location_id_name]
            geometry = self.model(
                name=name,
                geometry=GEOSGeometry(json.dumps(feature['geometry'])),
                properties=properties,
                location_id_name=location_id_name,
                location_id=location_id,
                **kwargs,
            )
            geometry.save(using=settings.SPATIAL_DB)
            ret.append(geometry)

        return ret


class Geometry(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)
    geometry = models.GeometryField(blank=True, null=True)
    properties = JSONField(default=dict)
    location_id_name = models.CharField(max_length=256, blank=True, null=True)
    location_id = models.CharField(max_length=256, blank=True, null=True)

    objects = GeometryManager()

    def to_dict(self):
        ret = {
            'type': 'Feature',
            'geometry': json.loads(self.geometry.geojson),
            'properties': self.properties,
        }

        return ret

    @property
    def geojson(self):
        return json.dumps(self.to_dict())


class DataSetManager(models.Manager):
    def create_from_json(self, name=None, file=None, location_id_name=None, **kwargs):
        if file is None or not file.name.endswith(('.geojson', '.json')):
            raise ValueError('Provide a json or geojson file.')

        geometries = Geometry.objects.create_from_json(file=file, location_id_name=location_id_name)
        data_set = self.model(
            name=name,
            type='FeatureCollection',
            geometry_collection=GEOSGeometryCollection(tuple(g.geometry for g in geometries)),
            location_id_name=location_id_name,
            **kwargs,
        )
        data_set.save(using=settings.SPATIAL_DB)
        data_set.geometries.set(geometries)

        return data_set


class DataSet(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)
    type = models.CharField(max_length=256, blank=True, null=True)
    geometries = models.ManyToManyField('spatial.Geometry', blank=True)
    geometry_collection = models.GeometryCollectionField(blank=True, null=True)
    location_id_name = models.CharField(max_length=256, unique=True, blank=True, null=True)

    objects = DataSetManager()

    def to_dict(self):
        ret = {
            'type': self.type,
            'features': [g.to_dict() for g in self.geometries.all()],
        }

        return ret

    @property
    def geojson(self):
        return json.dumps(self.to_dict())
