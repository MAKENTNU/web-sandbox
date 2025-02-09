from datetime import timedelta
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from users.models import User
from util.locale_utils import parse_datetime_localized
from util.test_utils import assertRaisesIntegrityError_withRollback, set_without_duplicates
from ...models import Article, Event, EventTicket, TimePlace


class ArticleEventAndTimePlaceTests(TestCase):

    @staticmethod
    def create_time_place(event, *, relative_publication_time, relative_start_time,
                          hidden=TimePlace._meta.get_field('hidden').default):
        now = timezone.localtime()
        start_time = now + timedelta(hours=relative_start_time)
        return TimePlace.objects.create(
            event=event,
            publication_time=now + timedelta(hours=relative_publication_time),
            start_time=start_time,
            end_time=start_time + timedelta(minutes=1),
            hidden=hidden,
        )

    def test_str(self):
        article = Article.objects.create(title="TEST_TITLE")
        self.assertEqual(article.title, "TEST_TITLE")
        self.assertEqual(article.title, str(article))

        title = "Test event"
        event = Event.objects.create(title=title)
        time_place = self.create_time_place(event, relative_publication_time=0, relative_start_time=0)
        date_str = timezone.localdate().strftime("%d.%m.%Y")
        self.assertEqual(str(time_place), f"{title} - {date_str}")

    def test_article_queryset(self):
        Article.objects.create(
            title="NOT PUBLISHED",
            publication_time=timezone.localtime() + timedelta(days=1),
        )
        Article.objects.create(
            title="NOT PUBLISHED",
            publication_time=timezone.localtime() + timedelta(seconds=1),
        )
        published1 = Article.objects.create(
            title="PUBLISHED",
            publication_time=timezone.localtime() - timedelta(days=1),
        )
        published2 = Article.objects.create(
            title="PUBLISHED",
            publication_time=timezone.localtime() - timedelta(seconds=1),
        )
        self.assertEqual(Article.objects.published().count(), 2)
        self.assertSetEqual(set(Article.objects.published()), {published1, published2})

    @mock.patch('django.utils.timezone.now')
    def test_event_queryset_correctly_filters_past_and_future_events(self, now_mock):
        now = parse_datetime_localized("2021-04-15 12:00")
        now_mock.return_value = now

        def create_event(event_type: Event.Type, title_and_relative_start_and_end_time_tuples: tuple[str, tuple[tuple[int, int], ...]]) -> Event:
            title, relative_start_and_end_time_tuples = title_and_relative_start_and_end_time_tuples
            event = Event.objects.create(
                title=f"{event_type.name.lower()}_{title}",
                event_type=event_type,
            )
            for relative_start_time, relative_end_time in relative_start_and_end_time_tuples:
                TimePlace.objects.create(
                    event=event,
                    publication_time=now + timedelta(days=1),  # publication time should not affect the `past()` or `future()` methods
                    start_time=now + timedelta(hours=relative_start_time),
                    end_time=now + timedelta(hours=relative_end_time),
                )
            return event

        def create_standalone(title_and_relative_start_and_end_time_tuples: tuple[str, tuple[tuple[int, int], ...]]) -> Event:
            return create_event(Event.Type.STANDALONE, title_and_relative_start_and_end_time_tuples)

        def create_repeating(title_and_relative_start_and_end_time_tuples: tuple[str, tuple[tuple[int, int], ...]]) -> Event:
            return create_event(Event.Type.REPEATING, title_and_relative_start_and_end_time_tuples)

        all_ended = ("all_ended", (
            (-3, -2),
            (-2, -1),
        ))
        some_ended_and_some_not_started = ("some_ended_and_some_not_started", (
            (-3, -2),
            (2, 3),
        ))
        some_ended_and_some_ongoing = ("some_ended_and_some_ongoing", (
            (-3, -2),
            (-1, 1),
        ))
        some_ongoing_and_some_not_started = ("some_ongoing_and_some_not_started", (
            (-1, 1),
            (2, 3),
        ))
        all_not_started = ("all_not_started", (
            (1, 2),
            (2, 3),
        ))
        none = ("none", ())

        standalone_with_all_ended = create_standalone(all_ended)
        standalone_with_some_ended_and_some_not_started = create_standalone(some_ended_and_some_not_started)
        standalone_with_some_ended_and_some_ongoing = create_standalone(some_ended_and_some_ongoing)
        standalone_with_some_ongoing_and_some_not_started = create_standalone(some_ongoing_and_some_not_started)
        standalone_with_all_not_started = create_standalone(all_not_started)
        standalone_with_none = create_standalone(none)

        repeating_with_all_ended = create_repeating(all_ended)
        repeating_with_some_ended_and_some_not_started = create_repeating(some_ended_and_some_not_started)
        repeating_with_some_ended_and_some_ongoing = create_repeating(some_ended_and_some_ongoing)
        repeating_with_some_ongoing_and_some_not_started = create_repeating(some_ongoing_and_some_not_started)
        repeating_with_all_not_started = create_repeating(all_not_started)
        repeating_with_none = create_repeating(none)

        past_events_set = set_without_duplicates(self, Event.objects.past())
        future_events_set = set_without_duplicates(self, Event.objects.future())
        self.assertSetEqual(past_events_set, {
            standalone_with_all_ended,
            repeating_with_all_ended, repeating_with_some_ended_and_some_not_started, repeating_with_some_ended_and_some_ongoing,
        })
        self.assertSetEqual(future_events_set, {
            standalone_with_some_ended_and_some_not_started,
            standalone_with_some_ended_and_some_ongoing,
            standalone_with_some_ongoing_and_some_not_started,
            standalone_with_all_not_started,

            repeating_with_some_ended_and_some_not_started,
            repeating_with_some_ended_and_some_ongoing,
            repeating_with_some_ongoing_and_some_not_started,
            repeating_with_all_not_started,
        })
        # Events with no timeplaces should not be counted among past or future events
        self.assertNotIn(standalone_with_none, past_events_set)
        self.assertNotIn(repeating_with_none, past_events_set)
        self.assertNotIn(standalone_with_none, future_events_set)
        self.assertNotIn(repeating_with_none, future_events_set)

    def test_timeplace_queryset(self):
        event = Event.objects.create(title="", hidden=False)
        hidden_event = Event.objects.create(title="", hidden=True)

        event_not_published = self.create_time_place(event, relative_publication_time=1, relative_start_time=1, hidden=False)
        event_future = self.create_time_place(event, relative_publication_time=-1, relative_start_time=1, hidden=False)
        event_past = self.create_time_place(event, relative_publication_time=-1, relative_start_time=-100, hidden=False)

        hidden_event_future_hidden = self.create_time_place(hidden_event, relative_publication_time=-1, relative_start_time=1)
        hidden_event_past_hidden = self.create_time_place(hidden_event, relative_publication_time=-1, relative_start_time=-1)
        hidden_event_future = self.create_time_place(hidden_event, relative_publication_time=-1, relative_start_time=1, hidden=False)
        hidden_event_past = self.create_time_place(hidden_event, relative_publication_time=-1, relative_start_time=-1, hidden=False)

        self.assertSetEqual(set(TimePlace.objects.published()), {event_future, event_past})
        self.assertSetEqual(set(TimePlace.objects.future()), {
            event_not_published, event_future, hidden_event_future_hidden, hidden_event_future,
        })
        self.assertSetEqual(set(TimePlace.objects.past()), {
            event_past, hidden_event_past_hidden, hidden_event_past,
        })
        self.assertSetEqual(set(TimePlace.objects.published().future()), {event_future})
        self.assertSetEqual(set(TimePlace.objects.published().past()), {event_past})


class EventTicketTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("user1")
        self.standalone_event = Event.objects.create(title="Standalone event", event_type=Event.Type.STANDALONE, number_of_tickets=10)
        self.repeating_event = Event.objects.create(title="Repeating event", event_type=Event.Type.REPEATING)
        self.standalone_time_place = TimePlace.objects.create(event=self.standalone_event, hidden=False)
        self.repeating_time_place = TimePlace.objects.create(event=self.repeating_event, hidden=False, number_of_tickets=10)

    def test_event_ticket_unique_constraints_are_enforced(self):
        self.assert_creating_ticket_raises_integrity_error(False, event=self.standalone_event, time_place=None)
        # Creating a second ticket with the same arguments should fail
        self.assert_creating_ticket_raises_integrity_error(True, event=self.standalone_event, time_place=None)

        self.assert_creating_ticket_raises_integrity_error(False, event=None, time_place=self.repeating_time_place)
        # Creating a second ticket with the same arguments should fail
        self.assert_creating_ticket_raises_integrity_error(True, event=None, time_place=self.repeating_time_place)

    def test_event_tickets_require_either_time_place_or_event_set(self):
        # Invalid combinations
        self.assert_creating_ticket_raises_integrity_error(True, event=None, time_place=None)
        self.assert_creating_ticket_raises_integrity_error(True, event=self.standalone_event, time_place=self.standalone_time_place)
        self.assert_creating_ticket_raises_integrity_error(True, event=self.repeating_event, time_place=self.repeating_time_place)
        self.assert_creating_ticket_raises_integrity_error(True, event=self.standalone_event, time_place=self.repeating_time_place)

        # Valid combinations
        self.assert_creating_ticket_raises_integrity_error(False, event=self.standalone_event, time_place=None)
        self.assert_creating_ticket_raises_integrity_error(False, event=None, time_place=self.repeating_time_place)

    def assert_creating_ticket_raises_integrity_error(self, raises: bool, *, event: Event | None, time_place: TimePlace | None):
        assertRaisesIntegrityError_withRollback(self,
                                                lambda: EventTicket.objects.create(user=self.user, event=event, timeplace=time_place),
                                                raises=raises)

    @mock.patch('django.utils.timezone.now')
    def test_event_tickets_have_equal__active_last_modified__and__creation_date__when_created(self, now_mock):
        now = parse_datetime_localized("2022-09-14 15:31")
        now_mock.return_value = now

        ticket = EventTicket.objects.create(user=self.user, event=self.standalone_event)
        self.assertEqual(ticket.creation_date, now)
        self.assertEqual(ticket.active_last_modified, ticket.creation_date)

        ticket = EventTicket.objects.create(user=self.user, timeplace=self.repeating_time_place)
        self.assertEqual(ticket.creation_date, now)
        self.assertEqual(ticket.active_last_modified, ticket.creation_date)
