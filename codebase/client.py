import base64
import json
import logging
import requests
import urllib2

from codebase import logger
from codebase.settings import Settings


class Auth(object):

    API_ENDPOINT = 'http://api3.codebasehq.com'

    def _default_settings(self):
        settings = Settings()
        self.username = settings.CODEBASE_USERNAME
        self.apikey = settings.CODEBASE_APIKEY

    def __init__(self, project, username=None, apikey=None, debug=False, **kwargs):
        super(Auth, self).__init__(**kwargs)

        if username and apikey:
            self.username = username
            self.apikey = apikey
        else:
            self._default_settings()

        self.project = project
        self.DEBUG = debug

        self.HEADERS = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization": base64.encodestring("%s:%s" % (self.username, self.apikey))\
                .replace('\n', '')
        }

        if debug:
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                datefmt='%m-%d %H:%M',
            )

    def get(self, url):
        response = requests.get(self.get_absolute_url(url), headers=self.HEADERS)
        return self.handle_response(response)

    def post(self, url, data):
        response = requests.post(self.get_absolute_url(url), data=json.dumps(data), headers=self.HEADERS)
        return self.handle_response(response)

    def handle_response(self, response):
        logger.debug('Response status code: {}'.format(response.status_code))
        if response.ok:
            return json.loads(response.content)
        else:
            return response.content

    def get_absolute_url(self, path):
        absolute_url = self.API_ENDPOINT + path
        logger.debug(absolute_url)
        return absolute_url


class CodeBaseAPI(Auth):

    def statuses(self):
        return self.get('/%s/tickets/statuses' % self.project)

    def priorities(self):
        return self.get('/%s/tickets/priorities' % self.project)

    def categories(self):
        return self.get('/%s/tickets/categories' % self.project)

    def milestones(self):
        return self.get('/%s/tickets/milestones' % self.project)

    def search(self, term):
        terms = term.split(':')
        if len(terms) == 1:
            escaped_term = urllib2.quote(terms[0])
        else:
            escaped_term = '{}:"{}"'.format(terms[0], urllib2.quote(terms[1]))
        return self.get('/%s/tickets?query=%s' % (self.project, escaped_term))

    def watchers(self, ticket_id):
        return self.get('/%s/tickets/%s/watchers' % (self.project, ticket_id))

    def project_groups(self):
        return self.get('/project_groups')

    def get_project_users(self):
        return self.get('/%s/assignments' % self.project)

    def set_project_users(self, data):
        return self.post('/%s/assignments' % self.project, data)

    def activity(self):
        return self.get('/activity')

    def project_activity(self):
        return self.get('/%s/activity' % self.project)

    def users(self):
        return self.get('/users')

    def roles(self):
        return self.get('/roles')

    def discussions(self):
        return self.get('/%s/discussions' % self.project)

    def discussion_categories(self):
        return self.get('/%s/discussions/categories' % self.project)

    def create_discussion(self, data):
        return self.post('/%s/discussions' % self.project, data)

    def posts_in_discussion(self, discussion_permalink):
        return self.get('/%s/discussions/%s/posts' % (self.project, discussion_permalink))

    def createpost_in_discussion(self, discussion_permalink, data):
        return self.post('/%s/discussions/%s/posts' % (self.project, discussion_permalink), data)

    def notes(self, ticket_id):
        return self.get('/%s/tickets/%s/notes' % (self.project, ticket_id))

    def note(self, ticket_id, note_id):
        return self.get('/%s/tickets/%s/notes/%s' % (self.project, ticket_id, note_id))

    def add_note(self, ticket_id, data):
        """
        data = {
            'ticket_note': {
                u'content': u'Another test',
                u'changes': {
                    u'status_id': u'1631923',
                },
            },
        }
        """
        return self.post('/%s/tickets/%s/notes' % (self.project, ticket_id), data)

    def branches(self, repository):
        return self.get('/%s/%s/branches' % (self.project, repository))

    def hooks(self, repository):
        return self.get('/%s/%s/hooks' % (self.project, repository))

    def add_hook(self, repository, data):
        return self.get('/%s/%s/hooks' % (self.project, repository), data)

