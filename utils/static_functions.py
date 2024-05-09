import json
import os

from data.users import User


def get_img(user):
    extensions = ['png', 'jpg', 'jpeg']
    img_src = 'static/img/def.png'
    if any([os.path.exists(f"static/img/{user.id}.{ext}") for ext in extensions]):
        img_src = list(filter(lambda y: os.path.exists(y), [f'static/img/{user.id}.{e}' for e in extensions]))[0]
    return img_src


def set_filters(query, idd):
    with open('filter_settings.json', 'r') as f:
        filters = json.load(f)
    if str(idd) in filters:
        user = filters[str(idd)]
        if user['age_from']:
            query = query.filter(User.age >= user['age_from'])
        if user['age_to']:
            query = query.filter(User.age <= user['age_to'])
        if user['school']:
            query = query.filter(User.school == user['school'])
        if user['tags']:
            query = query.filter(User.tags.contains(', '.join(user['tags'])))
    return query