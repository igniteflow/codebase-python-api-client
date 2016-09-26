from unittest import TestCase

from mock import call, patch

from codebase.utils import CodeBaseAPIUtils


@patch('codebase.client.CodeBaseAPI.post')
@patch('codebase.client.CodeBaseAPI.get')
@patch('codebase.client.CodeBaseAPI.search_all')
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

    def test_bulk_update_ticket_statuses(self, search_all_mock, get_mock, post_mock):
        search_all_mock.return_value = self.tickets_found
        get_mock.return_value = self.statuses

        # Bulk update the 5 tickets from 'New' to 'Completed'.
        bulk_res = self.api_client.bulk_update_ticket_statuses('New', 'Completed')
        self.assertEqual(
            bulk_res,
            [item['ticket']['ticket_id'] for item in self.tickets_found],
        )

        # Makes sure the first call retrieves the statuses, while the second
        # one searches for the 5 tickets.
        search_all_mock.assert_called_once_with(status='New')
        get_mock.assert_called_once_with(
            '/{}/tickets/statuses'.format(self.api_client.project)
        )
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
        self, logger_mock, search_all_mock, get_mock, post_mock
    ):
        search_all_mock.return_value = self.tickets_found
        get_mock.return_value = self.statuses

        # Trying to bulk update the 5 tickets, but using a non-existing status.
        bulk_res = self.api_client.bulk_update_ticket_statuses(
            'New',
            'Not a valid status',
        )
        self.assertIsNone(bulk_res)

        # Makes sure the first call retrieves the statuses, and there will
        # not be more calls because the status doesn't exit.
        get_mock.assert_called_once_with(
            '/{}/tickets/statuses'.format(self.api_client.project)
        )
        search_all_mock.assert_not_called()
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
