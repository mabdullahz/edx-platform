import copy
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from student.tests.factories import UserFactory

from openedx.features.philu_courseware.constants import COMP_ASSESS_RECORD_SUCCESS_MSG, INVALID_PROBLEM_ID_MSG

INVALID_ASSESSMENT_TYPE = 'This is invalid assessment type'
INVALID_CORRECTNESS = 'This is invalid correctness'
NOT_VALID_CHOICE_FORMAT = '"{}" is not a valid choice.'


class CompetencyAssessmentRecordTest(APITestCase):
    def setUp(self):
        self.user = UserFactory.create(username='testuser', password='testpwd')
        self.client.force_authenticate(self.user)
        self.end_point = reverse('record_competency_assessment')
        self.valid_record = {
            'problem_id': 'block-v1:PUCIT+IT1+1+type@problem+block@7f1593ef300e4f569e26356b65d3b76b',
            'problem_text': 'This is a problem',
            'assessment_type': 'pre',
            'attempt': 1,
            'correctness': 'correct',
            'choice_id': 1,
            'choice_text': 'This is correct choice',
            'score': 1
        }
        self.invalid_problem_id_record = {
            'problem_id': 'thisisinvalidproblemid',
            'problem_text': 'This is a problem',
            'assessment_type': 'pre',
            'attempt': 1,
            'correctness': 'correct',
            'choice_id': 1,
            'choice_text': 'This is correct choice',
            'score': 1
        }
        self.invalid_correctness_and_assessment_type_record = {
            'problem_id': 'block-v1:PUCIT+IT1+1+type@problem+block@7f1593ef300e4f569e26356b65d3b76b',
            'problem_text': 'This is a problem',
            'assessment_type': INVALID_ASSESSMENT_TYPE,
            'attempt': 1,
            'correctness': INVALID_CORRECTNESS,
            'choice_id': 1,
            'choice_text': 'This is correct choice',
            'score': 1
        }

    def test_valid_record(self):
        response = self.client.post(
            self.end_point,
            data=self.valid_record
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], COMP_ASSESS_RECORD_SUCCESS_MSG)

    def test_invalid_problem_id(self):
        response = self.client.post(
            self.end_point,
            data=self.invalid_problem_id_record
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(INVALID_PROBLEM_ID_MSG, response.data['message']['problem_id'])

    def test_invalid_correctness_and_assessment_type(self):
        response = self.client.post(
            self.end_point,
            data=self.invalid_correctness_and_assessment_type_record
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(NOT_VALID_CHOICE_FORMAT.format(INVALID_ASSESSMENT_TYPE), response.data['message']['assessment_type'])
        self.assertIn(NOT_VALID_CHOICE_FORMAT.format(INVALID_CORRECTNESS), response.data['message']['correctness'])

    def test_missing_keys(self):
        for key_to_miss in self.valid_record.keys():
            record = copy.copy(self.valid_record)
            record.pop(key_to_miss)
            self._assert_missing_keys(record, key_to_miss)

    def _assert_missing_keys(self, pay_load, missing_key):
        response = self.client.post(
            self.end_point,
            data=pay_load
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(missing_key, response.data['message'].keys())
        self.assertIn('This field is required.', response.data['message'][missing_key])
