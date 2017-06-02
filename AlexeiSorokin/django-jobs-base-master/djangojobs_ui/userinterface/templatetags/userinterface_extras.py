from django import template


register = template.Library()


@register.filter(name='replace')
def replace_space(value):
    try:
        value = value.replace(' ', '_')\
                .replace(',', '$').replace('.', '%').lower()
    except AttributeError:
        pass
    return value

