from django import template
from documentos.utils import protocolo_curto

register = template.Library()


@register.filter
def short_protocolo(value):
    return protocolo_curto(value)
