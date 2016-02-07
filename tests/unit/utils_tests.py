from unittest import TestCase
import urllib2

from mock import call, patch

from codebase.utils import CodeBaseAPIUtils


@patch('codebase.client.CodeBaseAPI.post')
@patch('codebase.client.CodeBaseAPI.get')
class CodeBaseAPIUtilsTestCase(TestCase):

    def setUp(self):
        super(CodeBaseAPIUtilsTestCase, self).setUp()

        self.api_client = CodeBaseAPIUtils(
            project='project',
            username='some/body',
            apikey='bees',
        )

        self.statuses = [
            {'ticketing_status': {'name': 'New', 'id': 1}},
            {'ticketing_status': {'name': 'Code Complete', 'id': 2}},
            {'ticketing_status': {'name': 'In Review', 'id': 3}},
            {'ticketing_status': {'name': 'Completed', 'id': 4}},
            {'ticketing_status': {'name': 'Invalid', 'id': 5}},
        ]
        self.tickets_found = [
            {'ticket': {'ticket_id': 12, 'summary': 'ticket 12'}},
            {'ticket': {'ticket_id': 34, 'summary': 'ticket 34'}},
            {'ticket': {'ticket_id': 56, 'summary': 'ticket 56'}},
            {'ticket': {'ticket_id': 78, 'summary': 'ticket 78'}},
            {'ticket': {'ticket_id': 90, 'summary': 'ticket 90'}},
        ]

    def test_bulk_update_ticket_statuses(self, get_mock, post_mock):
        # The first call should be get to `self.statuses`;
        # The second call should be get to `self.search`;
        get_mock.side_effect = [
            self.statuses,
            self.tickets_found,
        ]

        # What to expect from the calling to the search API.
        escaped_term = 'status:"{}"'.format(urllib2.quote('New'))
        expected_search_url = '/{}/tickets?query={}'.format(
            self.api_client.project,
            escaped_term,
        )

        # Bulk update the 5 tickets from 'New' to 'Completed'.
        bulk_res = self.api_client.bulk_update_ticket_statuses('New', 'Completed')
        self.assertEqual(bulk_res, True)

        # Makes sure the first call retrieves the statuses, while the second
        # one searches for the 5 tickets.
        get_mock.assert_has_calls([
            call('/{}/tickets/statuses'.format(self.api_client.project)),
            call(expected_search_url),
        ])
        # Makes sure the 5 tickets are updated, setting the status to
        # 'Completed' (status id = 4).
        post_mock.assert_has_calls([
            call(
                '/project/tickets/{}/notes'.format(item['ticket']['ticket_id']),
                {'ticket_note': {'changes': {'status_id': u'4'}}}
            )
            for item in self.tickets_found
        ])

    @patch('codebase.utils.logger')
    def test_bulk_update_ticket_statuses_no_status_found(
        self, logger_mock, get_mock, post_mock
    ):
        # The first call should be get to `self.statuses`;
        # The second call should be get to `self.search`;
        get_mock.side_effect = [
            self.statuses,
            self.tickets_found,
        ]

        # Trying to bulk update the 5 tickets, but using a non-existing status.
        bulk_res = self.api_client.bulk_update_ticket_statuses(
            'New',
            'Not a valid status',
        )
        self.assertEqual(bulk_res, False)

        # Makes sure the first call retrieves the statuses, and there will
        # not be more calls because the status doesn't exit.
        get_mock.assert_called_once_with(
            '/{}/tickets/statuses'.format(self.api_client.project)
        )
        # No calling to the post because the status doesn't exist.
        post_mock.assert_not_called()

        # Logger.
        available_statuses = ', '.join([
            'New',
            'Code Complete',
            'In Review',
            'Completed',
            'Invalid',
        ])
        logger_mock.info.assert_called_once_with(
            u'Status "Not a valid status" not found in project statuses. '
            u'Options are: {}'.format(available_statuses)
        )
