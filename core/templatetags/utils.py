from django.template.defaulttags import register


@register.filter
def get(dictionary, key):
    return dictionary.get(key)
