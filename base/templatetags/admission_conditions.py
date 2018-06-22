from django import template
from django.forms.utils import flatatt
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.html import format_html

register = template.Library()


def text_value(value):
    # credits Django-Bootstrap 3
    # https://github.com/dyve/django-bootstrap3/blob/master/bootstrap3/text.py#L11:5
    if value is None:
        return ''
    return force_text(value)


def render_tag(tag, attrs=None, content=None, close=True):
    # credits Django-Bootstrap 3
    # https://github.com/dyve/django-bootstrap3/blob/master/bootstrap3/utils.py#L129
    builder = '<{tag}{attrs}>{content}'
    if content or close:
        builder += '</{tag}>'
    return format_html(builder, tag=tag, attrs=mark_safe(flatatt(attrs)) if attrs else '',
                       content=text_value(content))


@register.simple_tag
def table_row_admission_line(tag_id, *args, **kwargs):
    return render_tag('tr', attrs={'id': tag_id})