import copy
import math
import pandas as pd
import re

from django.conf import settings
from django.db.models.fields.related import ManyToOneRel
from django.test import RequestFactory
from voto_studio_backend.changes.models import Change, Statistics, get_rels_dict_default
from voto_studio_backend.political.models import Individual, Law, Organization, Controversy
from voto_studio_backend.users.models import User


def name_regex(name):
    alias_regex = re.compile(r"'(\w*)'", re.DOTALL)
    try:
        raw_alias = re.search(alias_regex, name).group(0)
        alias = re.sub("'", '', raw_alias)
        full_name = re.sub(' ' + raw_alias, '', name)
    except AttributeError:
        alias = ''
        full_name = name

    return full_name, alias


def laws_regex(laws_string):
    try:
        separate_laws = laws_string.split('\n')
        law_number_regex = re.compile('(^Ley (\d+)?( /(\d+)))|(^Proyecto (\d+))( /(\d+))?(  /(\d+))?')
        laws_compendium = []
        for raw_law in separate_laws:
            try:
                full_meta = law_number_regex.match(raw_law).group(1)
                law_number = law_number_regex.match(raw_law).group(2)
                law_description = re.sub(full_meta, '', raw_law)
                law = {'law_number': law_number, 'law_description': law_description}
                laws_compendium.append(law)
            except AttributeError:
                print(f'Law did not match {raw_law}')
            except IndexError:
                print(f'Law did not match {raw_law}')
            except TypeError:
                print(f'Law did not match {raw_law}')
        return laws_compendium
    except AttributeError:
        print(f'Did not split {laws_string}')


def projects_regex(laws):
    try:
        law_number_regex = re.compile('^Proyecto de ley (\d+)( /(\d+))?')
        laws_compendium = []
        for raw_law in laws:
            try:
                full_meta = law_number_regex.match(raw_law).group(0)
                law_number = law_number_regex.match(raw_law).group(1)
                raw_law_description = re.sub(full_meta, '', raw_law)
                law_description = f'{raw_law_description[1].upper()}{raw_law_description[2:]}'
                law = {'law_number': law_number, 'law_description': law_description}
                laws_compendium.append(law)
            except AttributeError:
                print(f'Law did not match ATT {laws}')
            except IndexError:
                print(f'Laws did not match IND {laws}')
            except TypeError:
                print(f'Laws did not match TYPE {laws}')
        return laws_compendium
    except AttributeError:
        print(f'Oh Oh----------- {laws}')


def social_media_regex(full_url, domain):
    rs = f'(https?:\/\/)?((www|[a-z]{2}-[a-z]{2})\.)?{domain}\.com\/([A-Za-z0-9\.\-\_]{{5,}})\/?(\?(\w+=\w+&?)*)?$'
    res = re.compile(rs, re.IGNORECASE)

    return res.match(full_url).group(4)


def create_law_projects(data, user):
    print('Creating law projects...')
    request = RequestFactory()
    request.user = user
    laws = []

    for index, row in data.iterrows():
        print(f'{round(index/364*100, ndigits=3)}%')
        try:
            inner_laws = []
            for index, law_dict in enumerate(laws_regex(row['Law_Projects'])):
                print(f'Migrating law {index}...')
                law = Law.objects.create(
                    brief_description=law_dict['law_description'],
                    code=law_dict['law_number'],
                    user=user,
                    category=17,
                    source=row['Source']
                )
                base_law_instance = Change.objects.stage_created(law, request)
                inner_laws.append(base_law_instance)
            laws.append({'id': row['id'], 'laws': inner_laws})
        except TypeError:
            pass

    return laws


class TrackedError(Exception):
    pass


def create_controversies(data, user):
    print('Creating controversies...')
    request = RequestFactory()
    request.user = user

    first_individual_id = Individual.objects.filter(user=user).first().id

    for index, row in data.iterrows():
        print(f'{round(index/520*100, ndigits=3)}%')
        id_ = first_individual_id+3*(row['id']-1)
        individual = Individual.objects.get(id=id_)

        if not individual.tracked:
            raise TrackedError(f"Instance {individual} is not tracked!")

        controversy = Controversy.objects.create(
            brief_description=row['controversias'],
            source=row['source'] if isinstance(row['source'], str) else None,
            type=17,
            user=user,
        )

        # A dict that defines all the fks can be added
        # to ES only after the migrations have been done.
        individual.controversies.add(controversy)
        individual.add_rel(individual._meta.get_field('controversies'), controversy)

        base_controversy = Change.objects.stage_created(controversy, request)


def create_orgs(data, user):
    print('Creating orgs...')
    request = RequestFactory()
    request.user = user

    for index, row in data.iterrows():
        print(f'{round(index/71*100, ndigits=3)}%')
        try:
            org, new = Organization.objects.get_or_create(
                name=row['Political_Party_Name'],
                user=user,
                type=2,
            )
        except:
            new = False

        if new:
            base_org = Change.objects.stage_created(org, request)


def parse_data(data, user):
    print('Migrating rows...')
    individuals = []
    request = RequestFactory()
    request.user = user
    for index, row in data.iterrows():
        print(f'-------------------------------------------------------------')
        print(f'Migrating row {index}        {round(index/71*100, ndigits=3)}%')
        print(f'-------------------------------------------------------------\n')
        data = {}
        if isinstance(row['Facebook'], str) and len(row['Facebook']) > 5:
            data['facebook_username'] = social_media_regex(row['Facebook'], 'facebook')
        else:
            data['facebook_username'] = ''

        if isinstance(row['Twitter'], str) and len(row['Twitter']) > 5:
            data['twitter_username'] = social_media_regex(row['Twitter'], 'twitter')
        else:
            data['twitter_username'] = ''

        data['name'], data['alias'] = name_regex(row['Politician'])

        individual = Individual.objects.create(
            name=data['name'],
            alias=data['alias'],
            facebook_username=data['facebook_username'],
            twitter_username=data['twitter_username'],
            type=1,
            user=user,
            location_id_name='CIRCUITO',
            location_id=row['Circuito'],
        )

        statistics = Statistics()()

        statistics['sub_instances'].append({
            'id': '1',
            'fields': [
                {'name': 'id', 'value': '1'},
                {'name': 'name', 'value': 'Leyes_Propuestas'},
                {'name': 'value', 'value': str(row['Leyes_Propuestas'])},
                {'name': 'icon', 'value': 'gavel'},
            ]
        })
        statistics['sub_instances'].append({
            'id': '2',
            'fields': [
                {'name': 'id', 'value': '2'},
                {'name': 'name', 'value': 'Asistencia'},
                {'name': 'value', 'value': str(row['Asistencia'])},
                {'name': 'icon', 'value': 'percent'},
            ]
        })
        statistics['sub_instances'].append({
            'id': '3',
            'fields': [
                {'name': 'id', 'value': '3'},
                {'name': 'name', 'value': 'Circuito'},
                {'name': 'value', 'value': str(row['Circuito'])},
                {'name': 'icon', 'value': 'map-marked-alt'},
            ]
        })
        statistics['sub_instances'].append({
            'id': '4',
            'fields': [
                {'name': 'id', 'value': '4'},
                {'name': 'name', 'value': 'Periodos'},
                {'name': 'value', 'value': str(row['Periodos'])},
                {'name': 'icon', 'value': 'calendar-alt'},
            ]
        })

        individual.statistics = statistics
        try:
            individual.save()
        except:
            individual.statistics = None
            individual.save()

        base_instance = Change.objects.stage_created(individual, request)

        org = Organization.objects.get(name=row['Political_Party_Name'], tracked=True)
        org.individuals.add(base_instance)
        org.add_rel(Organization._meta.get_field('individuals'), base_instance)
        base_org = Change.objects.stage_updated(org, request)

        laws = []
        try:
            for index, law_dict in enumerate(laws_regex(row['Leyes'])):
                print(f'Migrating law {index}...')
                law, new = Law.objects.get_or_create(code=law_dict['law_number'], tracked=True)
                law.brief_description = law_dict['law_description']
                law.user = user
                law.category = 17,
                law.save(to_index=False)

                base_law_instance = Change.objects.stage_created(law, request)
                laws.append(base_law_instance)
        except TypeError:
            pass

        individuals.append(base_instance)

        base_instance.laws.set(laws)
        for law in laws:
            base_instance.add_rel(Individual._meta.get_field('laws'), law)
        base_instance = Change.objects.stage_updated(base_instance, request)


def migrate(user='migration@bot.com'):
    try:
        user = User.objects.create_user(
            email=user,
            name='Migration Bot',
            password='Migrate123',
        )
    except:
        user = User.objects.get(email='migration@bot.com')

    data = pd.read_excel('data/final_diputados.xlsx', sheet_name=0)

    create_orgs(data, user)
    parse_data(data, user)

    data = pd.read_excel('data/final_diputados.xlsx', sheet_name=1)

    create_controversies(data, user)


FIELD_MODEL_MAP = {
    'financial_items': 'political.FinancialItem',
    'individuals': 'political.Individual',
    'organizations': 'political.Organization',
    'laws': 'political.Law',
    'electoral_periods': 'political.ElectoralPeriod',
    'corruption_cases': 'political.CorruptionCase',
    'controversies': 'political.Controversy',
    'informative_snippets': 'corruption.InformativeSnippet',
    'promises': 'political.Promise',
    'achievements': 'political.Achievements',
    'images': 'media.Image',
    'videos': 'media.Video',
    'resources': 'media.Resource',
}


class UpdateError(Exception):
    pass


def update_rels_dict(model_class, using=settings.STUDIO_DB):
    user = User.objects.get(email='migration@bot.com')
    request = RequestFactory()
    request.user = user
    instances = model_class.objects.using(using).filter(tracked=True)
    if not instances.count():
        raise UpdateError(f"No '{model_class._meta.label}' instances")
    for index, instance in enumerate(instances):
        if not index % math.ceil(instances.count() / 10):
            print(f'{round(index / instances.count() * 100)}%')
        rels_dict = copy.deepcopy(instance.rels_dict)
        for key in list(rels_dict.keys()):
            if not FIELD_MODEL_MAP[key].startswith('media'):
                rels_dict[key].update({
                    'model_label': FIELD_MODEL_MAP[key],
                    'type': instance._meta.get_field(key).get_internal_type(),
                })
            else:
                rels_dict.pop(key)

        if not instance.rels_dict == rels_dict:
            print('Updating rels_dict on ', instance)
            instance.rels_dict = rels_dict
            instance.save(using=settings.STUDIO_DB)
            Change.objects.stage_updated(instance, request)
    print('100%')


def add_new_fields_to_rels_dict(model_class, using=settings.STUDIO_DB):
    instances = model_class.objects.using(using).filter(tracked=True)
    # instances = [model_class.objects.get(id=4572)]
    if not instances.count():
        raise UpdateError(f"No '{model_class._meta.label}' instances")
    for index, instance in enumerate(instances):
        if not index % math.ceil(instances.count() / 10):
            print(f'{round(index / instances.count() * 100)}%')
        rels_dict = instance.rels_dict
        for field in model_class.objects._get_fields():
            if field.name not in rels_dict.keys():
                rels_dict.update({field.name: get_rels_dict_default(field=field)})
            else:
                field_type = field.get_internal_type()
                inner_rels_dict = get_rels_dict_default(field=field)
                if field_type == 'OneToOneField':
                    id_ = getattr(getattr(instance, field.name, None), 'id', None)
                    inner_rels_dict['id'] = id_
                elif field_type == 'ForeignKey':
                    if isinstance(field, ManyToOneRel):
                        ids = [obj.id for obj in getattr(instance, f'{field.name}_set').filter(tracked=True)]
                    else:
                        ids = getattr(getattr(instance, field.name, None), 'id', None)
                        ids = [ids] if ids is not None else []
                    inner_rels_dict['ids'] = ids
                elif field_type == 'ManyToManyField':
                    ids = [obj.id for obj in getattr(instance, field.name).all()]
                    inner_rels_dict['rels'] = ids

                rels_dict[field.name] = inner_rels_dict

        instance.rels_dict = rels_dict
        instance.save(using=using)
    print('100%')


def remove_field_from_rels_dict(model_class, field_name):
    instances = model_class.objects.filter(tracked=True)
    if not instances.count():
        raise UpdateError(f"No '{model_class._meta.label}' instances")
    for index, instance in enumerate(instances):
        if not index % math.ceil(instances.count() / 10):
            print(f'{round(index / instances.count() * 100)}%')
        rels_dict = instance.rels_dict
        try:
            del rels_dict[field_name]
            print(f"Deleted {field_name} on instance with ID {instance.id} ------------------------------------------")
        except KeyError:
            print(f"Instance with ID {instance.id} didn't have key {field_name} in rels_dict.")

        instance.rels_dict = rels_dict
        instance.save(using=settings.STUDIO_DB)
    print('100%')
