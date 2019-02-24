import math
import pandas as pd
import re

from django.conf import settings
from django.test import RequestFactory
from voto_studio_backend.changes.models import Change, Statistics
from voto_studio_backend.political.models import Individual, Law, Organization, Controversy
from voto_studio_backend.users.models import User


def name_regex(name):
    alias_regex = re.compile(r"'(\w*)'", re.DOTALL)
    try:
        raw_alias = re.search(alias_regex, name).group(0)
        alias = re.sub("'", "", raw_alias)
        full_name = re.sub(" " + raw_alias, "", name)
    except AttributeError:
        alias = ""
        full_name = name

    return full_name, alias


def laws_regex(laws_string):
    try:
        # Extract info regex
        separate_laws = laws_string.split('\n')
        law_number_regex = re.compile("(^Ley (\d+))|(^Proyecto (\d+))( /(\d+))?(  /(\d+))?")
        laws_compendium = []
        for raw_law in separate_laws:
            try:
                full_meta = law_number_regex.match(raw_law).group(1)
                law_number = law_number_regex.match(raw_law).group(2)
                law_description = re.sub(full_meta, "", raw_law)
                law = {'law_number' : law_number, 'law_description': law_description}
                laws_compendium.append(law)
            except AttributeError:
                print("Law did not match" + raw_law)
                pass
            except IndexError:
                print("Laws did not match" + raw_law)
                pass
            except TypeError:
                print("Laws did not match" + raw_law)
                pass
        return laws_compendium
    except AttributeError:
        print("Did not split ")
        print(laws_string)
        pass


def projects_regex(laws):
    try:
        law_number_regex = re.compile("^Proyecto de ley (\d+)( /(\d+))?")
        laws_compendium = []
        for raw_law in laws:
            try:
                full_meta = law_number_regex.match(raw_law).group(0)
                law_number = law_number_regex.match(raw_law).group(1)
                raw_law_description = re.sub(full_meta, "", raw_law)
                law_description = "%s%s" % (raw_law_description[1].upper(), raw_law_description[2:])
                law = {'law_number': law_number, 'law_description': law_description}
                laws_compendium.append(law)
            except AttributeError:
                print("Law did not match ATT")
                print(laws)
                pass
            except IndexError:
                print("Laws did not match IND ")
                print(laws)
                pass
            except TypeError:
                print("Laws did not match TYPE")
                print(laws)
                pass
        return laws_compendium
    except AttributeError:
        print("Oh Oh----------- ")
        print(laws)


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
                    long_description=law_dict['law_description'],
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


def create_controversies(data, user):
    print('Creating controversies...')
    request = RequestFactory()
    request.user = user

    first_individual_id = Individual.objects.all().order_by('id')[0].id

    for index, row in data.iterrows():
        print(f'{round(index/520*100, ndigits=3)}%')
        individual = Individual.objects.get(id=first_individual_id + row['id'])

        controversy = Controversy.objects.create(
            brief_description=row['controversias'],
            source=row['source'] if isinstance(row['source'], str) else None,
            type=17,
            user=user,
        )

        # A dict that defines all the fks can be added
        # to ES only after the migrations have been done.
        controversy.individual = individual
        controversy.save()

        base_controversy = Change.objects.stage_created(controversy, request)
        base_individual = Change.objects.stage_updated(individual, request)


def create_orgs(data, user):
    print('Creating orgs...')
    request = RequestFactory()
    request.user = user

    for index, row in data.iterrows():
        print(f'{round(index/71*100, ndigits=3)}%')
        data = {}
        try:
            org = Organization.objects.create(
                name=row['Political_Party_Name'],
                user=user,
                type=2,
            )
            base_org = Change.objects.stage_created(org, request)
        except:
            pass


default_statistics = Statistics()()


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

        org = Organization.objects.get(name=row['Political_Party_Name'])
        org.individuals.add(base_instance)
        org.add_rel(Organization._meta.get_field('individuals'), base_instance)
        base_org = Change.objects.stage_updated(org, request)

        laws = []
        try:
            for index, law_dict in enumerate(laws_regex(row['Leyes'])):
                print(f'Migrating law {index}...')
                law = Law.objects.create(
                    long_description=law_dict['law_description'],
                    code=law_dict['law_number'],
                    user=user,
                    location_id_name='CIRCUITO',
                    location_id=row['Circuito'],
                    category=17,
                )
                base_law_instance = Change.objects.stage_created(law, request)
                laws.append(base_law_instance)
        except TypeError:
            pass

        individuals.append(base_instance)

        base_instance.laws.set(laws)
        for law in laws:
            base_instance.add_rel(Individual._meta.get_field('laws'), law)
        base_instance = Change.objects.stage_updated(base_instance, request)
        base_law_instances = Change.objects.bulk_stage_updated(laws, request)


def migrate():
    try:
        user = User.objects.create_user(
            email='migration@bot.com',
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
    'informative_snippets': 'corruption.InformativeSnippet',
    'images': 'media.Image',
    'videos': 'media.Video',
    'resources': 'media.Resource',
}


class UpdateError(Exception):
    pass


def update_rels_dict(model_class):
    user = User.objects.get(email='migration@bot.com')
    request = RequestFactory()
    request.user = user
    instances = model_class.objects.filter(tracked=True)
    if not instances.count():
        raise UpdateError(f"No '{model_class._meta.label}' instances")
    for index, instance in enumerate(instances):
        if not index % math.ceil(instances.count() / 10):
            print(f'{round(index / instances.count() * 100)}%')
        rels_dict = instance.rels_dict
        for key in list(rels_dict.keys()):
            if not FIELD_MODEL_MAP[key].startswith('media'):
                rels_dict[key].update({'model_label': FIELD_MODEL_MAP[key]})
            else:
                rels_dict.pop(key)

        instance.rels_dict = rels_dict
        instance.save(using=settings.STUDIO_DB)
        Change.objects.stage_updated(instance, request)
    print('100%')
