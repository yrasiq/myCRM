from django import template
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal


register = template.Library()

@register.filter
def keyvalue(dict, key):
    try:
        if dict[key] is None:
            dict[key] = ''
        return dict[key]
    except KeyError:
        return ''

@register.filter
def getattrvalue(obj, attr):
    value = getattr(obj, attr, '')
    if isinstance(value, ContentType):
        return value.name
    elif value is None:
        return ''
    elif attr == 'phone':
        return '+7' + value
    else:
        return value

@register.filter
def getclassname(obj) -> str:
    return obj.__class__.__name__

@register.filter
def remdivision(obj, number):
    return obj % number

@register.filter
def field_by_number(obj, number):
    for i, value in enumerate(obj):
        if i == number:
            return value

@register.filter
def to_decimal(num):
    if num:
        return round(Decimal(num), 2)
    else:
        return None
