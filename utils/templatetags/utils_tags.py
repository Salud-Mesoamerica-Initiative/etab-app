# -*- coding: utf-8 -*-
import json

from django import template
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.query import QuerySet
from django.forms.models import model_to_dict

register = template.Library()


@register.filter
def to_json(obj, arg=None):
    if isinstance(obj, (list, dict, tuple, set)):
        to_dumps = obj
    elif isinstance(obj, QuerySet):
        fields = []
        if arg:
            fields = arg.replace(' ', '').split(',')
        obj = obj.values(*fields)
        to_dumps = list(obj)
    elif isinstance(obj, bool):
        return 'true' if obj else 'false'
    else:
        to_dumps = []
        str_type = str(type(obj))
        if 'model' in str_type:
            try:
                to_dumps = model_to_dict(obj, exclude=['user'])
            except:
                pass

    try:
        json_result = json.dumps(to_dumps, cls=DjangoJSONEncoder)
    except:
        json_result = json.dumps([], cls=DjangoJSONEncoder)
    return json_result