##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.db import models
from django.contrib import admin
from base.models import text_label
from base.models.exceptions import FunctionAgrumentMissingException, FunctionTxtLabelExitsException

FUNCTIONS = 'functions'


class TranslatedTextLabelAdmin(admin.ModelAdmin):
    list_display = ('label', 'language', 'text_label',)
    fieldsets = ((None, {'fields': ('label', 'language', 'text_label')}),)
    search_fields = ['acronym']


class TranslatedTextLabel(models.Model):
    label = models.CharField(max_length=255)
    language = models.ForeignKey('reference.Language')
    text_label = models.ForeignKey('TextLabel')

    def save(self, *args, **kwargs):
        if FUNCTIONS not in kwargs.keys():
            raise FunctionAgrumentMissingException('The kwarg "{0}" must be set.'.format(FUNCTIONS))
        functions = kwargs.pop(FUNCTIONS)

        if self.text_label:
            foundtxtlabel = text_label.TextLabel.objects.filter(entity_name=self.text_label.entity_name,
                                                                label=self.text_label.label,
                                                                order=self.text_label.order)
            if foundtxtlabel.count() == 0:
                raise FunctionTxtLabelExitsException('A text label is required')

        super(TranslatedTextLabel, self).save(*args, **kwargs)
        for function in functions:
            function(self)

    def __str__(self):
        return 'Label : ' + self.label + ' - Language ' + str(self.language.code) + ' - Text_Label (Parent) : ' + self.text_label.label


def find_by_id(translated_text_label_id):
    return TranslatedTextLabel.objects.get(pk=translated_text_label_id)


def find_by_ids(translated_text_label_ids):
    return TranslatedTextLabel.objects.filter(pk__in=translated_text_label_ids)


def find_by_language(language_input):
    queryset = TranslatedTextLabel.objects.filter(language__code=language_input)
    return queryset


def search(acronym=None):
    queryset = TranslatedTextLabel.objects

    if acronym:
        queryset = queryset.filter(acronym=acronym)

    return queryset

