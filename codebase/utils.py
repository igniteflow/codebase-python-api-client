import sys

from codebase import logger
from codebase.client import CodeBaseAPI


class CodeBaseAPIUtils(CodeBaseAPI):

    def bulk_update_ticket_statuses(self, current_status_name, target_status_name):

        # get the status ids because Codebase search doesn't support searching on status id
        new_status_id = None
        statuses = self.statuses()

        for status in statuses:
            if status['ticketing_status']['name'] == target_status_name:
                new_status_id = status['ticketing_status']['id']

        # exit if the ticket status was not found
        if target_status_name is None:
            logger.info('Status {} not found in project statuses.  Options are: {}'.format(
                [status['ticketing_status']['name'] for status in statuses]
            ))

        # update the tickets
        items = self.search('status:{}'.format(current_status_name))
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
            sys.stdout.write('[{}] {} {} --> {}'.format(
                ticket_id,
                item['ticket']['summary'],
                current_status_name,
                target_status_name
            ))