from django.test import TestCase

from base.models.admission_condition import AdmissionCondition
from base.tests.factories.education_group_year import EducationGroupYearFactory
from webservices.tests.helper import Helper


class WsGetAdmissionsConditionsTestCase(TestCase, Helper):
    URL_NAME = 'ws_get_cond_admissions'

    def test_get(self):
        education_group_year = EducationGroupYearFactory()
        admission_condition = AdmissionCondition.objects.create(education_group_year=education_group_year)

        iso_language, language = 'fr-be', 'fr'

        response = self.post(education_group_year.academic_year.year,
                             language,
                             education_group_year.acronym,
                             data={})

        print(response)

        # self.assertEqual(response.status_code, 200)