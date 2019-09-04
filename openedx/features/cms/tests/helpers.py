import time

from datetime import datetime
from pytz import UTC

from openedx.features.cms import helpers
from cms.djangoapps.contentstore.tests.test_courseware_index import COURSE_CHILD_STRUCTURE
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory
from lms.djangoapps.courseware.courses import get_course_by_id

RUBRIC_ASSESSMENTS = [
    {
        "start": None,
        "due": None,
        "name": "student-training"
    },
    {
        "must_be_graded_by": 3,
        "start": "2019-03-01T00:00",
        "due": "2019-04-01T00:00",
        "must_grade": 5,
        "name": "peer-assessment"
    },
    {
        "start": "2019-05-01T00:00:00+0000",
        "due": "2019-06-01T00:00:00+0000",
        "name": "self-assessment"
    },
    {
        "start": "2019-07-01T00:00:00+0000",
        "due": "2019-08-01T00:00:00+0000",
        "required": False,
        "name": "staff-assessment"
    }
]


def create_source_course(store, user, course_start_date):
    """
    Create a source course as an input for test cases. Re-runs will be created from this course.
    """
    course = CourseFactory.create(modulestore=store, start=course_start_date)
    with store.bulk_operations(course.id):
        # chapter1, Session and subsection with same start date
        create_children(store, course, "chapter", 1, start_date=course_start_date)

    # chapter2, Session and subsection with different dates
    chapter2 = ItemFactory.create(
        parent_location=course.location,
        category="chapter",
        display_name="chapter with two sequential",
        modulestore=store,
        publish_item=True,
        start=datetime(2019, 10, 1, tzinfo=UTC),
    )
    # sequential 1 in chapter 2, with due date
    sequential1_chapter2 = ItemFactory.create(
        parent_location=chapter2.location,
        category="sequential",
        display_name="sequential 1",
        modulestore=store,
        publish_item=True,
        due=datetime(2019, 10, 20, tzinfo=UTC),
        start=datetime(2019, 10, 10, tzinfo=UTC),
    )
    # sequential 2 in chapter 2, without due date
    ItemFactory.create(
        parent_location=chapter2.location,
        category="sequential",
        display_name="sequential 2",
        modulestore=store,
        publish_item=True,
        start=datetime(2019, 11, 1, tzinfo=UTC),
    )
    # Vertical 1 in sequential 1 of chapter 2
    vertical1_sequential1_chapter2 = ItemFactory.create(
        parent_location=sequential1_chapter2.location,
        category="vertical",
        display_name="vertical 1",
        modulestore=store,
        publish_item=True,
    )
    # Ora 1 in Vertical 1 of sequential 1 of chapter 2
    ora1_vertical1_sequential1_chapter2 = ItemFactory.create(
        parent_location=vertical1_sequential1_chapter2.location,
        category="openassessment",
        display_name="ORA - all custom dates",
        name="ora1",
        modulestore=store,
        publish_item=True,
        metadata={
            'submission_start': '2019-01-01T00:00',
            'submission_due': '2019-02-01T00:00',
        }
    )
    ora1_vertical1_sequential1_chapter2.rubric_assessments = RUBRIC_ASSESSMENTS
    helpers.component_update(ora1_vertical1_sequential1_chapter2, user)

    # Ora 2 in Vertical 1 of sequential 1 of chapter 2
    ora2_vertical1_sequential1_chapter2 = ItemFactory.create(
        parent_location=vertical1_sequential1_chapter2.location,
        category="openassessment",
        display_name="ORA - default assessment dates",
        name="ora2",
        modulestore=store,
        publish_item=True,
        metadata={
            'submission_start': '2019-01-01T00:00',
            'submission_due': '2019-02-01T00:00',
        }
    )

    # Chapter 3 having no sequential
    ItemFactory.create(
        parent_location=course.location,
        category="chapter",
        display_name="Empty chapter",
        modulestore=store,
        publish_item=True,
        start=datetime(2019, 11, 1, tzinfo=UTC),
    )

    return get_course_by_id(course.id)


def create_children(store, parent, category, load_factor,
                    start_date=datetime(2019, 1, 1, tzinfo=UTC)):
    """
    create load_factor children within the given parent; recursively call to insert children
    when appropriate
    """
    created_count = 0
    for child_index in range(load_factor):
        child_object = ItemFactory.create(
            parent_location=parent.location,
            category=category,
            display_name=u"{} {} {}".format(category, child_index, time.clock()),
            modulestore=store,
            publish_item=True,
            start=start_date,
        )
        created_count += 1

        if category in COURSE_CHILD_STRUCTURE:
            created_count += create_children(store, child_object, COURSE_CHILD_STRUCTURE[category],
                                             load_factor, start_date=start_date)

    return created_count


def create_large_course(store, load_factor, start_date=datetime(2019, 1, 1, tzinfo=UTC)):
    """
    Create a large course, note that the number of blocks created will be
    load_factor ^ 4 - e.g. load_factor of 10 => 10 chapters, 100
    sequentials, 1000 verticals, 10000 html blocks
    """
    course = CourseFactory.create(modulestore=store, start=start_date)
    with store.bulk_operations(course.id):
        child_count = create_children(store, course, "chapter", load_factor)
    return course, child_count
