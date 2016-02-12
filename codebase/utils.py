import sys

from codebase import logger
from codebase.client import CodeBaseAPI


class CodeBaseAPIUtils(CodeBaseAPI):

    def bulk_update_ticket_statuses(self, current_status_name, target_status_name):
        """
        Example usage to set all "Approved for Dev" tp "Deployed to Dev":

        STATUS_TRANSITIONS = {
            'dev': ('Approved for Dev', 'Deployed to Dev'),
            'uat': ('Approved for UAT', 'Deployed to UAT'),
            'prod': ('Approved for Prod', 'Deployed to Prod'),
        }

        env = 'dev'
        current_status_name = STATUS_TRANSITIONS[env][0]
        target_status_name = STATUS_TRANSITIONS[env][1]
        codebase_utils.bulk_update_ticket_statuses(current_status_name, target_status_name)
        """

        # get the status ids because Codebase search doesn't support searching on status id
        new_status_id = None
        statuses = self.statuses()

        for status in statuses:
            if status['ticketing_status']['name'] == target_status_name:
                new_status_id = status['ticketing_status']['id']

        # exit if the ticket status was not found
        if new_status_id is None:
            status_names = ', '.join([
                status['ticketing_status']['name'] for status in statuses
            ])
            logger.info(
                u'Status "{}" not found in project statuses. '
                u'Options are: {}'.format(target_status_name, status_names)
            )
            return False

        # update the tickets
        items = self.search_all(status=current_status_name)
        for item in items:
            ticket_id = item['ticket']['ticket_id']
            data = {
                'ticket_note': {
                    u'changes': {
                        u'status_id': unicode(new_status_id),
                    },
                },
            }
            self.add_note(ticket_id, data)

            # print output
            sys.stdout.write('[{}] {} {} --> {}\n'.format(
                ticket_id,
                item['ticket']['summary'],
                current_status_name,
                target_status_name
            ))

        return True
