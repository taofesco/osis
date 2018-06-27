import textwrap

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def render_condition_rows(section_name, header_text, records):
    content = [render_header_table(header_text, section_name)]

    for record in records:
        content.append(render_row(record, section_name))

    return mark_safe(''.join(content))


def render_row(record, section_name):
    row = """
        <tr id="{section}_{record_id}">
            <td id="{section}_{record_id}_diploma">{diploma}</td>
            <td id="{section}_{record_id}_conditions">{conditions}</td>
            <td id="{section}_{record_id}_access" class="text-right">{access}</td>
            <td id="{section}_{record_id}_remarks">{remarks}</td>
            <td class="text-right">
                <a href="#" role="button" data-record-id="{record_id}" data-section="{section}" class="button line-remove-btn">
                    <span class="glyphicon glyphicon-remove-circle" style="font-size: 16px;" aria-hidden="true">
                    </span>
                </a>
                <a href="#" role="button" class="button line-edit-btn" data-record-id="{record_id}" data-section="{section}">
                    <span class="glyphicon glyphicon-edit" style="font-size: 16px;" aria-hidden="true"></span>
                </a>
            </td>
        </tr>
    """.format(section=section_name,
               record_id=record.id,
               diploma=record.diploma,
               conditions=mark_safe(record.conditions),
               access=mark_safe(record.access),
               remarks=mark_safe(record.remarks))
    return textwrap.dedent(row)


def render_header_table(header_text, section_name):
    header = """
        <tr id="{section_name}">
            <td colspan="5" class="info">
                {header_text} <a class="button line-add-btn" data-section="{section_name}" href="#">
                <span class="glyphicon glyphicon-plus" aria-hidden="true"></span>
                </a>
            </td>
        </tr>
    """.format(section_name=section_name, header_text=header_text)
    return textwrap.dedent(header)

@register.inclusion_tag('templatetags/admission_condition_text.html')
def render_condition_text(section_name, text, field):
    return {
        'section': section_name,
        'text': text,
        'field': field,
    }
