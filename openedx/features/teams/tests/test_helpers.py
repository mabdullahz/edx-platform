import factory

from django.conf import settings
from django.db.models import signals

from lms.djangoapps.onboarding.tests.factories import UserFactory
from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

from openedx.features.teams.tests.factories import CourseTeamFactory
from openedx.features.teams.serializers import CustomCourseTeamCreationSerializer
from openedx.features.teams.helpers import (
    USER_ICON_COLORS,
    TEAM_BANNER_COLORS,
    generate_random_user_icon_color,
    generate_random_team_banner_color,
    make_embed_url,
    serialize,
    get_user_recommended_team,
    get_user_course_with_access,
    get_team_topic
)


USER_COUNTRY = 'US'


class HelpersTestCase(ModuleStoreTestCase):
    """ Tests for all helpers in teams module."""

    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def setUp(self):
        """ Setup data required for the following test cases """
        super(HelpersTestCase, self).setUp()
        self.topics = self._create_topics()
        self.course = self._create_course()
        self.team = self._create_team(self.course.id, self.course.teams_topics[0]['id'])
        self.user = UserFactory.create(profile__country=USER_COUNTRY)

    def _create_topics(self):
        """ Return dummy topics data """
        return [
            {u'name': u'Topic', u'description': u'The first best topic!', u'id': u'0', 'url': 'example.com/topic/0'},
            {u'name': u'Topic', u'description': u'The second best topic!', u'id': u'1', 'url': 'example.com/topic/1'},
        ]

    def _create_course(self):
        """ Create and return test course """
        org = 'edX'
        course_number = 'CS101'
        course_run = '2015_Q1'
        display_name = 'test course 1'
        course = CourseFactory.create(
            org=org,
            number=course_number,
            run=course_run,
            display_name=display_name,
            default_store=ModuleStoreEnum.Type.split,
            teams_configuration={
                "max_team_size": 10,
                "topics": self.topics
            }
        )
        return course

    def _create_team(self, course_id, topic_id):
        """ Create and return a CourseTeam for provided Course with provided course_id
        and Topic with provided topic_id

        Arguments:
            course_id {int} -- Id of the course for which the team is to be generated
            topic_id {int} --Id of the topic for which the team is to be generated

        Returns:
            CourseTeam
        """
        team = CourseTeamFactory.create(
            course_id=course_id,
            topic_id=topic_id,
            name='Test Team',
            description='Testing Testing Testing...',
        )
        return team

    def _create_team_membership(self, team, user):
        """Create a team membership object that is responsible for joining of a user in a team.

        Arguments:
            team {CourseTeam} -- Team to join
            user {User} -- User who is going to join the team

        Returns:
            CourseTeamMembership
        """
        membership = CourseTeamMembershipFactory.create(team=team, user=user)
        return membership

    def test_generate_random_user_icon_color(self):
        """ Test that the icon color generated is from valid colors list. """
        color = generate_random_user_icon_color()
        self.assertIn(color, USER_ICON_COLORS)

    def test_generate_random_team_banner_color(self):
        """ Test that the team banner color generated is from valid colors list. """
        color = generate_random_team_banner_color()
        self.assertIn(color, TEAM_BANNER_COLORS)

    def test_make_embed_url_with_topic_url(self):
        """ Test that correct embed url is generated when topic_url is provided and no team_group_chat is given"""
        embed_url = make_embed_url(team_group_chat=None, user=self.user, topic_url=self.topics[0]['url'])
        expected_output = '{}/embed/{}?iframe=embedView&isTopic=True'.format(settings.NODEBB_ENDPOINT, self.topics[0]['id'])
        self.assertEqual(embed_url, expected_output)

    def test_make_embed_url_with_team_group_chat(self):
        """ Test that correct embed url is generated when no topic_url is provided but team_group_chat is given"""
        team_group_chat = self.team.team.all().first()
        embed_url = make_embed_url(team_group_chat=team_group_chat, user=self.user, topic_url=None)
        expected_output = '{}/category/{}?iframe=embedView'.format(settings.NODEBB_ENDPOINT, team_group_chat.slug)
        self.assertEqual(embed_url, expected_output)

    def test_make_embed_url_with_only_user(self):
        """ Test that correct embed url is generated when no topic_url is provided and slug value for
        team_group_chat is empty
        """
        team_group_chat = self.team.team.all().first()
        team_group_chat.slug = ''
        embed_url = make_embed_url(team_group_chat=team_group_chat, user=self.user, topic_url=None)
        expected_output = '{}/user/{}/chats/{}?iframe=embedView'.format(
            settings.NODEBB_ENDPOINT, self.user.username, team_group_chat.room_id
        )
        self.assertEqual(embed_url, expected_output)

    def test_serialize(self):
        """ Test that a team object is serialized correctly with given request and context.
        Values of serialized data are compared with that of matching keys in actual data
        """
        data = self.team.__dict__
        dummy_request = {}
        dummy_context = {'test_context': 'test_value'}
        serialized_data = serialize(
            data,
            serializer_cls=CustomCourseTeamCreationSerializer,
            serializer_ctx=dummy_context,
            request=dummy_request,
            many=False
        )
        serialized_data_keys = serialized_data.keys()
        expected_data = {key: str(data[key]) for key in serialized_data_keys}
        self.assertEqual(serialized_data, expected_data)

    def test_get_user_recommended_teams(self):
        """ Test that the helper method returns user recommended teams bases on
        user country. Teams in which user is enrolled should not be returned.
        """
        expected_result = [self.team, ]
        actual_result = get_user_recommended_team(self.course.id, self.user)
        self.assertEqual(actual_result, expected_result)

    def test_get_user_course_with_access(self):
        """ Test that user can access the course """
        result = get_user_course_with_access(self.course.id.__str__(), self.user)
        self.assertEqual(result, self.course)

    def test_get_team_topic(self):
        """ Test that `get_team_topic` returns the topic with matching topic_id form
        current course team topics """
        result = get_team_topic(self.course, self.topics[0]['id'])
        self.assertEqual(result, self.topics[0])
