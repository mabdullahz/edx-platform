"""Defines serializers used by the Team API."""
from lms.djangoapps.teams.serializers import (
    CourseTeamCreationSerializer, CountryField, CourseTeamSerializer, UserMembershipSerializer
)
from rest_framework import serializers
from django.conf import settings

from .helpers import generate_random_team_banner_color, generate_random_user_icon_color


class CustomCountryField(CountryField):
    """
    Field to serialize a country code.
    """

    def to_internal_value(self, data):
        """
        Check that the code is a valid country code.

        We leave the data in its original format so that the Django model's
        CountryField can convert it to the internal representation used
        by the django-countries library.
        """

        if not data:
            raise serializers.ValidationError(
                "Country field is required"
            )

        if data and data not in self.COUNTRY_CODES:
            raise serializers.ValidationError(
                u"{code} is not a valid country code".format(code=data)
            )
        return data


class CustomLanguageField(serializers.Field):
    """
    Field to serialize a Language code.
    """

    LANGUAGE_CODES = dict(settings.ALL_LANGUAGES).keys()

    def to_representation(self, obj):
        """
        Represent the country as a 2-character unicode identifier.
        """
        return unicode(obj)

    def to_internal_value(self, data):
        """
        Check that the code is a valid language code.

        We leave the data in its original format so that the Django model's
        CountryField can convert it to the internal representation used
        by the django-countries library.
        """

        if not data:
            raise serializers.ValidationError(
                "Language field is required"
            )

        if data and data not in self.LANGUAGE_CODES:
            raise serializers.ValidationError(
                u"{code} is not a valid language code".format(code=data)
            )
        return data


class CustomCourseTeamCreationSerializer(CourseTeamCreationSerializer):
    country = CustomCountryField(required=True)
    language = CustomLanguageField(required=True)


class CustomUserMembershipSerializer(UserMembershipSerializer):
    class Meta(object):
        model = UserMembershipSerializer.Meta.model
        fields = UserMembershipSerializer.Meta.fields + ('profile_color',)
        read_only_fields = UserMembershipSerializer.Meta.read_only_fields

    profile_color = serializers.SerializerMethodField()

    def get_profile_color(self, membership):
        return generate_random_user_icon_color()


class CustomCourseTeamSerializer(CourseTeamSerializer):
    country = serializers.SerializerMethodField()
    language = serializers.SerializerMethodField()
    banner_color = serializers.SerializerMethodField()
    membership = CustomUserMembershipSerializer(many=True, read_only=True)

    class Meta(object):
        model = CourseTeamSerializer.Meta.model
        fields = CourseTeamSerializer.Meta.fields + ('banner_color',)
        read_only_fields = CourseTeamSerializer.Meta.read_only_fields

    def get_country(self, course_team):
        return course_team.country.name.format()

    def get_language(self, course_team):
        languages = dict(settings.ALL_LANGUAGES)
        try:
            return languages[course_team.language]
        except KeyError:
            return course_team.language

    def get_banner_color(self, course_team):
        return generate_random_team_banner_color()
