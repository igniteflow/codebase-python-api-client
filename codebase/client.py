import base64
import json
import logging
import urllib
import urllib2
import urlparse

import xmltodict

from codebase import logger
from codebase.settings import Settings


class Auth(object):
    CTYPE_JSON = 'json'
    CTYPE_XML = 'xml'
    API_ENDPOINT = 'https://api3.codebasehq.com'

    def __init__(self, project=None, username=None, apikey=None, **kwargs):
        super(Auth, self).__init__(**kwargs)

        if not (username or apikey):
            settings = self._get_settings()
            username = settings.username
            apikey = settings.apikey

        self.username = username
        self.apikey = apikey

        self.project = project

    def _get_settings(self):
        settings = Settings()
        settings.import_settings()
        return settings

    def get_absolute_url(self, path):
        return urlparse.urljoin(self.API_ENDPOINT, path)

    def get_headers(self, ctype):
        return {
            'Content-type': 'application/{}'.format(ctype),
            'Accept': 'application/{}'.format(ctype),
            'Authorization': base64.b64encode(
                '{}:{}'.format(self.username, self.apikey)
            )
        }

    def get_data(self, raw_data, ctype):
        if ctype == self.CTYPE_XML:
            return xmltodict.unparse(raw_data)

        # Encodes the parameters by default (i.e. using json).
        return urllib.urlencode(raw_data)

    def _handle_response(self, response, ctype):
        try:
            status_code = response.getcode()
            content = response.read()
            logger.debug('{} returned status code {}'.format(
                response.url,
                status_code
            ))

            if ctype == self.CTYPE_XML:
                return xmltodict.parse(content)
            return json.loads(content)
        except Exception as e:
            logging.exception('%s: %s', e.__class__.__name__, e.message)

    def _send_request(self, url, ctype=None, data=None):
        if not ctype:
            ctype = self.CTYPE_JSON

        absolute_url = self.get_absolute_url(url)
        headers = self.get_headers(ctype)
        req_params = {
            'url': absolute_url,
            'headers': headers,
        }
        if data:
            data = self.get_data(data, ctype)
            req_params['data'] = data

        request = urllib2.Request(**req_params)
        logging.info('Making request to {} with headers {}'.format(
            request.get_full_url(),
            request.headers,
        ))

        response = urllib2.urlopen(request)
        return self._handle_response(response, ctype)

    def get(self, url, ctype=None):
        return self._send_request(url, ctype=ctype)

    def post(self, url, data, ctype=None):
        return self._send_request(url, data=data, ctype=ctype)


class CodeBaseAPI(Auth):

    def projects(self):
        return self.get('/projects')

    def statuses(self):
        return self.get('/%s/tickets/statuses' % self.project)

    def priorities(self):
        return self.get('/%s/tickets/priorities' % self.project)

    def categories(self):
        return self.get('/%s/tickets/categories' % self.project)

    def types(self):
        return self.get('/%s/tickets/types' % self.project)

    def milestones(self):
        return self.get('/%s/milestones' % self.project)

    def search(self, term=None, page=None, **kwargs):
        queries = []
        if term:
            queries.append(term.strip())

        for term_name, term_value in kwargs.iteritems():
            if term_name.startswith('not_'):
                term_name = term_name.replace('not_', 'not-')
            queries.append('{}:"{}"'.format(term_name, term_value.strip()))

        params = {'query': ' '.join(queries)}
        if page and page > 1 and type(page) is int:
            params['page'] = page

        url = '/{}/tickets?{}'.format(self.project, urllib.urlencode(params))
        return self.get(url)

    def search_all(self, term=None, **kwargs):
        page = 1
        tickets = []
        while True:
            try:
                tickets.extend(self.search(term=term, page=page, **kwargs))
                page += 1
            except urllib2.HTTPError:
                page -= 1
                break
            except Exception, e:
                logger.error(
                    u'An error occured while searching for "%s" '
                    u'(current page: %s):\n%s', term, page, e
                )
                page -= 1
                break

        return tickets

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

    def create_ticket(self, data):
        # It looks like that only XML requests are accepted for creating new
        # tickets.
        return self.post(
            '/%s/tickets' % self.project,
            data,
            ctype=self.CTYPE_XML,
        )

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
        return self.post('/%s/%s/hooks' % (self.project, repository), data)
