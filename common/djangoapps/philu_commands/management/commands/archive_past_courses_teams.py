"""
Django management command to archive course community on nodeBB.
"""
from pytz import utc
from logging import getLogger
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from lms.djangoapps.branding import get_visible_courses
from common.djangoapps.nodebb.helpers import archive_course_community


log = getLogger(__name__)


class Command(BaseCommand):
    help = """
    This command picks all courses that end in the past 24 hours and archives the course discussion community for 
    it in nodebb (which archives all mini communities)
    example:
        manage.py ... archive_past_courses_teams
    """

    def handle(self, *args, **options):
        courses = get_visible_courses()
        time_to_compare_with = datetime.utcnow().replace(tzinfo=utc)
        days_seconds = timedelta(days=1).total_seconds()

        for course in courses:
            if not course.end:
                continue

            # To check if the course has ended between the last 24 hours
            time_diff_in_seconds = (time_to_compare_with - course.end).total_seconds()

            if 0 < time_diff_in_seconds < days_seconds:
                log.info('Archiving course community for course id: {}'.format(course.id))
                archive_course_community(course.id)
