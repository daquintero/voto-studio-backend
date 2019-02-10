import math
import pandas as pd
import re

from django.test import RequestFactory
from voto_backend.changes.models import Change
from voto_backend.political.models import Individual, Law, Organization, Controversy
from voto_backend.users.models import User


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


def laws_regex(law_string):
    try:
        separate_laws = law_string.split('\n')
        law_number_regex = re.compile("^Ley (\d+)( /(\d+))|(  /(\d+))")
        laws_compendium = []
        for raw_law in separate_laws:
            try:
                full_meta = law_number_regex.match(raw_law).group(0)
                law_number = law_number_regex.match(raw_law).group(1)
                law_description = re.sub(full_meta, "", raw_law)
                law = {'law_number' : law_number, 'law_description': law_description}
                laws_compendium.append(law)
            except AttributeError:
                # print("Oh ----------- " + raw_law)
                pass
            except IndexError:
                # print("Oh ----------- " + raw_law)
                pass
        return laws_compendium
    except AttributeError:
        # print(laws_array)
        pass


def projects_regex(law_string):
    try:
        law_number_regex = re.compile("^Proyecto de ley (\d+)|( /(\d+))")
        laws_compendium = []
        for raw_law in law_string:
            try:
                full_meta = law_number_regex.match(raw_law).group(0)
                law_number = law_number_regex.match(raw_law).group(1)
                raw_law_description = re.sub(full_meta, "", raw_law)
                law_description = "%s%s" % (raw_law_description[1].upper(), raw_law_description[2:])
                law = {'law_number' : law_number, 'law_description': law_description}
                laws_compendium.append(law)
            except AttributeError:
                print("Oh ----------- " + raw_law)
            except IndexError:
                print("Oh ----------- " + raw_law)
        return laws_compendium
    except AttributeError:
        print("Oh Oh----------- " + law_string)


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

        statistics = []
        statistics.append({'icon': 'home', 'name': 'Leyes_Propuestas', 'value': str(row['Leyes_Propuestas'])})
        statistics.append({'icon': 'plane', 'name': 'Asistencia', 'value': str(row['Asistencia'])})
        statistics.append({'icon': 'wrench', 'name': 'Circuito', 'value': str(row['Circuito'])})
        statistics.append({'icon': 'spinner', 'name': 'Periodos', 'value': str(row['Periodos'])})

        individual.statistics = statistics
        try:
            individual.save()
        except:
            individual.statistics = None
            individual.save()

        base_instance = Change.objects.stage_created(individual, request)

        org = Organization.objects.get(name=row['Political_Party_Name'])
        org.individuals.add(base_instance)
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
        user = User.objects.get(id=1)

    data = pd.read_excel('data/final_diputados.xlsx', sheet_name=0)

    create_orgs(data, user)
    parse_data(data, user)

    data = pd.read_excel('data/final_diputados.xlsx', sheet_name=1)

    create_controversies(data, user)
