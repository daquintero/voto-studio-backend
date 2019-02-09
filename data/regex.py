import re

from django.test import RequestFactory
from voto_backend.changes.models import Change
from voto_backend.political.models import Individual


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


def laws_regex(laws_array):
    try:
        separate_laws = laws_array.split('\n')
        law_number_regex = re.compile("^Ley (\d+)|( /(\d+))")
        laws_compendium = []
        for raw_law in separate_laws:
            try:
                full_meta = law_number_regex.match(raw_law).group(0)
                law_number = law_number_regex.match(raw_law).group(1)
                law_description = re.sub(full_meta, "", raw_law)
                law = {'law_number': law_number, 'law_description': law_description}
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


def social_media_regex(full_url, domain):
    rs = f'(https?:\/\/)?((www|[a-z]{2}-[a-z]{2})\.)?{domain}\.com\/([A-Za-z0-9\.\-\_]{{5,}})\/?(\?(\w+=\w+&?)*)?$'
    res = re.compile(rs, re.IGNORECASE)

    return res.match(full_url).group(4)


def parse_data(data, user):
    individuals = []
    request = RequestFactory()
    request.user = user
    for index, row in data.iterrows():
        data = {}
        if isinstance(row['Facebook'], str) and len(row['Facebook']) > 5:
            data['facebook_username'] = social_media_regex(row['Facebook'], 'facebook')
        else:
            data['facebook_username'] = ''

        if isinstance(row['Twitter'], str) and len(row['Twitter']) > 5:
            data['twitter_username'] = social_media_regex(row['Twitter'], 'twitter')
        else:
            data['twitter_username'] = ''

        data['name'], data['alias'] = name_regex(row['Diputado'])

        individual = Individual.objects.create(
            name=data['name'],
            alias=data['alias'],
            facebook_username=data['facebook_username'],
            twitter_username=data['twitter_username'],
            type=1,
            user=user,
        )

        base_instance = Change.objects.stage_created(individual, request)
        individuals.append(base_instance)

    return individuals
