from unittest import TestCase
import base64
import json
import urllib
import urllib2
import urlparse

from mock import Mock, patch
import xmltodict

from codebase.client import Auth, CodeBaseAPI


class AuthInitTestCase(TestCase):

    @patch(
        'codebase.client.Auth._get_settings',
        return_value=Mock(username='foo', apikey='bar')
    )
    def test_init_credentials_ignores_get_settings(self, get_settings_mock):
        auth = Auth(project='project', username='some/body', apikey='bees')

        get_settings_mock.assert_not_called()
        self.assertEqual(auth.project, 'project')
        self.assertEqual(auth.username, 'some/body')
        self.assertEqual(auth.apikey, 'bees')

    @patch(
        'codebase.client.Auth._get_settings',
        return_value=Mock(username='foo', apikey='bar')
    )
    def test_init_credentials_calls_get_settings(self, get_settings_mock):
        auth = Auth(project='project')

        get_settings_mock.assert_called_once_with()
        self.assertEqual(auth.project, 'project')
        self.assertEqual(auth.username, 'foo')
        self.assertEqual(auth.apikey, 'bar')

    @patch('codebase.client.Settings', return_value=Mock(username='foo', apikey='bar'))
    def test_settings_ignored_on_init(self, settings_mock):
        instance = settings_mock.return_value

        # Sanity check.
        settings_mock.assert_not_called()
        instance.import_settings.assert_not_called()

        # Creating the object.
        auth = Auth(project='project', username='some/body', apikey='bees')

        settings_mock.assert_not_called()
        instance.import_settings.assert_not_called()

        self.assertEqual(auth.project, 'project')
        self.assertEqual(auth.username, 'some/body')
        self.assertEqual(auth.apikey, 'bees')

    @patch('codebase.client.Settings', return_value=Mock(username='foo', apikey='bar'))
    def test_settings_used_on_init(self, settings_mock):
        instance = settings_mock.return_value

        # Sanity check.
        settings_mock.assert_not_called()
        instance.import_settings.assert_not_called()

        # Creating the object.
        auth = Auth(project='project')

        settings_mock.assert_called_once_with()
        instance.import_settings.assert_called_once_with()
        self.assertEqual(auth.project, 'project')
        self.assertEqual(auth.username, 'foo')
        self.assertEqual(auth.apikey, 'bar')


class AuthTestCase(TestCase):

    def setUp(self):
        super(AuthTestCase, self).setUp()

        self.base_api_url = 'https://api3.codebasehq.com'
        self.auth_client = Auth(
            project='project',
            username='some/body',
            apikey='bees',
        )

    def _create_fake_response(self, data, ctype=None, code=200):
        # Does not change the data if ctype is different than json or xml
        # (useful if we want to throw an error).
        content = data
        if ctype == 'xml':
            content = xmltodict.unparse(data)
        elif ctype == 'json':
            content = json.dumps(data)

        return Mock(
            getcode=Mock(return_value=code),
            read=Mock(return_value=content),
            url='http://theurl.com',
        )

    def test_get_absolute_url(self):
        path = '/the/resource/'
        expected_url = urlparse.urljoin(self.base_api_url, path)
        self.assertEqual(self.auth_client.get_absolute_url(path), expected_url)

    def test_get_headers(self):
        for ctype in ['json', 'xml']:
            expected_headers = {
                'Content-type': 'application/{}'.format(ctype),
                'Accept': 'application/{}'.format(ctype),
                'Authorization': base64.b64encode('{}:{}'.format(
                    self.auth_client.username, self.auth_client.apikey
                )),
            }
            self.assertEqual(
                self.auth_client.get_headers(ctype),
                expected_headers,
            )

    def test_get_data_json(self):
        data = {'something': 'to send', 'to': 'codebase'}
        self.assertEqual(
            self.auth_client.get_data(data, 'json'),
            urllib.urlencode(data),
        )
        self.assertEqual(
            self.auth_client.get_data(data, 'blabla'),
            urllib.urlencode(data),
        )

    def test_get_data_xml(self):
        data = {'theroot': {'something': 'to send', 'to': 'codebase'}}
        self.assertEqual(
            self.auth_client.get_data(data, 'xml'),
            xmltodict.unparse(data),
        )

    @patch('codebase.client.logger')
    def test_handle_response_json(self, logger_mock):
        data = {'something': 'to send', 'to': 'codebase'}
        response = self._create_fake_response(data, ctype='json')

        handled_response = self.auth_client._handle_response(response, 'json')

        self.assertEqual(handled_response, data)
        response.getcode.assert_called_once_with()
        response.read.assert_called_once_with()
        logger_mock.debug.assert_called_once_with(
            'http://theurl.com returned status code 200'
        )

    @patch('codebase.client.logger')
    def test_handle_response_xml(self, logger_mock):
        data = {'theroot': {'something': 'to send', 'to': 'codebase'}}
        response = self._create_fake_response(data, ctype='xml')

        handled_response = self.auth_client._handle_response(response, 'xml')

        self.assertEqual(handled_response, data)
        response.getcode.assert_called_once_with()
        response.read.assert_called_once_with()
        logger_mock.debug.assert_called_once_with(
            'http://theurl.com returned status code 200'
        )

    @patch('codebase.client.logging')
    @patch('codebase.client.logger')
    def test_handle_response_error(self, logger_mock, logging_mock):
        data = 'this is not a valid json'
        response = self._create_fake_response(data)

        handled_response = self.auth_client._handle_response(response, 'json')

        self.assertIsNone(handled_response)
        response.getcode.assert_called_once_with()
        response.read.assert_called_once_with()
        logger_mock.debug.assert_called_once_with(
            'http://theurl.com returned status code 200'
        )
        logging_mock.exception.assert_called_once_with(
            '%s: %s', 'ValueError', 'No JSON object could be decoded'
        )

    @patch('codebase.client.urllib2.urlopen')
    @patch('codebase.client.urllib2.Request')
    def test_send_request_default(self, urllib_req_mock, urllib_urlopen_mock):
        response_data = {'data': 1}
        response_fake = self._create_fake_response(response_data, ctype='json')
        urllib_urlopen_mock.return_value = response_fake
        resource_path = 'the/url/to/the/resource'

        response = self.auth_client._send_request(resource_path)

        self.assertEqual(response, response_data)
        urllib_urlopen_mock.assert_called_once_with(urllib_req_mock.return_value)
        urllib_req_mock.assert_called_once_with(
            url=urlparse.urljoin(self.base_api_url, resource_path),
            headers=self.auth_client.get_headers('json'),
        )

    @patch('codebase.client.urllib2.urlopen')
    @patch('codebase.client.urllib2.Request')
    def test_send_request_json(self, urllib_req_mock, urllib_urlopen_mock):
        response_data = {'data': 1}
        response_fake = self._create_fake_response(response_data, ctype='json')
        urllib_urlopen_mock.return_value = response_fake
        resource_path = 'the/url/to/the/resource'

        response = self.auth_client._send_request(resource_path, ctype='json')

        self.assertEqual(response, response_data)
        urllib_urlopen_mock.assert_called_once_with(urllib_req_mock.return_value)
        urllib_req_mock.assert_called_once_with(
            url=urlparse.urljoin(self.base_api_url, resource_path),
            headers=self.auth_client.get_headers('json'),
        )

    @patch('codebase.client.urllib2.urlopen')
    @patch('codebase.client.urllib2.Request')
    def test_send_request_xml(self, urllib_req_mock, urllib_urlopen_mock):
        response_data = {'root': 'the value'}
        response_fake = self._create_fake_response(response_data, ctype='xml')
        urllib_urlopen_mock.return_value = response_fake
        resource_path = 'the/url/to/the/resource'

        response = self.auth_client._send_request(resource_path, ctype='xml')

        self.assertEqual(dict(response), response_data)
        urllib_urlopen_mock.assert_called_once_with(urllib_req_mock.return_value)
        urllib_req_mock.assert_called_once_with(
            url=urlparse.urljoin(self.base_api_url, resource_path),
            headers=self.auth_client.get_headers('xml'),
        )

    @patch('codebase.client.urllib2.urlopen')
    @patch('codebase.client.urllib2.Request')
    def test_send_request_error(self, urllib_req_mock, urllib_urlopen_mock):
        response_data = 'invalid xml'
        response_fake = self._create_fake_response(response_data)
        urllib_urlopen_mock.return_value = response_fake
        resource_path = 'the/url/to/the/resource'

        response = self.auth_client._send_request(resource_path, ctype='xml')

        self.assertIsNone(response)
        urllib_urlopen_mock.assert_called_once_with(urllib_req_mock.return_value)
        urllib_req_mock.assert_called_once_with(
            url=urlparse.urljoin(self.base_api_url, resource_path),
            headers=self.auth_client.get_headers('xml'),
        )

    @patch('codebase.client.urllib2.urlopen')
    @patch('codebase.client.urllib2.Request')
    def test_send_request_data(self, urllib_req_mock, urllib_urlopen_mock):
        response_data = {'response': 1}
        request_data = {'request': 2}
        response_fake = self._create_fake_response(response_data, ctype='json')
        urllib_urlopen_mock.return_value = response_fake
        resource_path = 'the/url/to/the/resource'

        response = self.auth_client._send_request(resource_path, data=request_data)

        self.assertEqual(response, response_data)
        urllib_urlopen_mock.assert_called_once_with(urllib_req_mock.return_value)
        urllib_req_mock.assert_called_once_with(
            url=urlparse.urljoin(self.base_api_url, resource_path),
            headers=self.auth_client.get_headers('json'),
            data=self.auth_client.get_data(request_data, 'json')
        )

    @patch('codebase.client.Auth._send_request')
    def test_get_default(self, send_request_mock):
        data = {'data': 1}
        send_request_mock.return_value = data
        resource_path = 'the/url/to/the/resource'

        response = self.auth_client.get(resource_path)

        self.assertEqual(response, data)
        send_request_mock.assert_called_once_with(resource_path, ctype=None)

    @patch('codebase.client.Auth._send_request')
    def test_get_ctype(self, send_request_mock):
        data = {'data': 1}
        send_request_mock.return_value = data
        resource_path = 'the/url/to/the/resource'

        response = self.auth_client.get(resource_path, ctype='json')

        self.assertEqual(response, data)
        send_request_mock.assert_called_once_with(resource_path, ctype='json')

    @patch('codebase.client.Auth._send_request')
    def test_post_default(self, send_request_mock):
        data_response = {'response': 1}
        data_request = {'request': 2}
        send_request_mock.return_value = data_response
        resource_path = 'the/url/to/the/resource'

        response = self.auth_client.post(resource_path, data_request)

        self.assertEqual(response, data_response)
        send_request_mock.assert_called_once_with(
            resource_path,
            data=data_request,
            ctype=None,
        )

    @patch('codebase.client.Auth._send_request')
    def test_post_ctype(self, send_request_mock):
        data_response = {'response': 1}
        data_request = {'request': 2}
        send_request_mock.return_value = data_response
        resource_path = 'the/url/to/the/resource'

        response = self.auth_client.post(resource_path, data_request, ctype='json')

        self.assertEqual(response, data_response)
        send_request_mock.assert_called_once_with(
            resource_path,
            data=data_request,
            ctype='json',
        )


@patch('codebase.client.CodeBaseAPI.post')
@patch('codebase.client.CodeBaseAPI.get')
class CodeBaseAPITestCase(TestCase):

    def setUp(self):
        super(CodeBaseAPITestCase, self).setUp()

        self.api_client = CodeBaseAPI(
            project='project',
            username='some/body',
            apikey='bees',
        )

    def test_get_projects(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        self.api_client.projects()

        get_mock.assert_called_once_with('/projects')
        post_mock.assert_not_called()

    def test_statuses(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        expected_url = '/{}/tickets/statuses'.format(self.api_client.project)
        self.api_client.statuses()

        get_mock.assert_called_once_with(expected_url)
        post_mock.assert_not_called()

    def test_priorities(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        expected_url = '/{}/tickets/priorities'.format(self.api_client.project)
        self.api_client.priorities()

        get_mock.assert_called_once_with(expected_url)
        post_mock.assert_not_called()

    def test_categories(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        expected_url = '/{}/tickets/categories'.format(self.api_client.project)
        self.api_client.categories()

        get_mock.assert_called_once_with(expected_url)
        post_mock.assert_not_called()

    def test_types(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        expected_url = '/{}/tickets/types'.format(self.api_client.project)
        self.api_client.types()

        get_mock.assert_called_once_with(expected_url)
        post_mock.assert_not_called()

    def test_milestones(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        expected_url = '/{}/milestones'.format(self.api_client.project)
        self.api_client.milestones()

        get_mock.assert_called_once_with(expected_url)
        post_mock.assert_not_called()

    def test_search_simple_term(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        term = 'something interesting'
        expected_url = '/{}/tickets?query={}'.format(
            self.api_client.project,
            urllib2.quote(term),
        )

        self.api_client.search(term)

        get_mock.assert_called_once_with(expected_url)
        post_mock.assert_not_called()

    def test_search_complex_term(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        term = 'something:more interesting'
        escaped_term = 'something:"{}"'.format(urllib2.quote('more interesting'))
        expected_url = '/{}/tickets?query={}'.format(
            self.api_client.project,
            escaped_term,
        )

        self.api_client.search(term)

        get_mock.assert_called_once_with(expected_url)
        post_mock.assert_not_called()

    def test_watchers(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        expected_url = '/{}/tickets/12/watchers'.format(self.api_client.project)

        self.api_client.watchers(12)

        get_mock.assert_called_once_with(expected_url)
        post_mock.assert_not_called()

    def test_project_groups(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        self.api_client.project_groups()

        get_mock.assert_called_once_with('/project_groups')
        post_mock.assert_not_called()

    def test_get_project_users(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        expected_url = '/{}/assignments'.format(self.api_client.project)
        self.api_client.get_project_users()

        get_mock.assert_called_once_with(expected_url)
        post_mock.assert_not_called()

    def test_set_project_users(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        data = {'some_data': 'some-value'}
        expected_url = '/{}/assignments'.format(self.api_client.project)
        self.api_client.set_project_users(data)

        get_mock.assert_not_called()
        post_mock.assert_called_once_with(expected_url, data)

    def test_activity(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        self.api_client.activity()

        get_mock.assert_called_once_with('/activity')
        post_mock.assert_not_called()

    def test_project_activity(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        expected_url = '/{}/activity'.format(self.api_client.project)
        self.api_client.project_activity()

        get_mock.assert_called_once_with(expected_url)
        post_mock.assert_not_called()

    def test_users(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        self.api_client.users()

        get_mock.assert_called_once_with('/users')
        post_mock.assert_not_called()

    def test_roles(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        self.api_client.roles()

        get_mock.assert_called_once_with('/roles')
        post_mock.assert_not_called()

    def test_discussions(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        expected_url = '/{}/discussions'.format(self.api_client.project)
        self.api_client.discussions()

        get_mock.assert_called_once_with(expected_url)
        post_mock.assert_not_called()

    def test_discussion_categories(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        expected_url = '/{}/discussions/categories'.format(self.api_client.project)
        self.api_client.discussion_categories()

        get_mock.assert_called_once_with(expected_url)
        post_mock.assert_not_called()

    def test_create_ticket(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        data = {'some_data': 'some-value'}
        expected_url = '/{}/tickets'.format(self.api_client.project)
        self.api_client.create_ticket(data)

        get_mock.assert_not_called()
        post_mock.assert_called_once_with(
            expected_url,
            data,
            ctype='xml'
        )

    def test_create_discussion(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        data = {'some_data': 'some-value'}
        expected_url = '/{}/discussions'.format(self.api_client.project)
        self.api_client.create_discussion(data)

        get_mock.assert_not_called()
        post_mock.assert_called_once_with(expected_url, data)

    def test_posts_in_discussion(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        permalink = 'something-to-point-to'
        expected_url = '/{}/discussions/{}/posts'.format(
            self.api_client.project,
            permalink,
        )
        self.api_client.posts_in_discussion(permalink)

        get_mock.assert_called_once_with(expected_url)
        post_mock.assert_not_called()

    def test_createpost_in_discussion(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        data = {'some_data': 'some-value'}
        permalink = 'something-to-point-to'
        expected_url = '/{}/discussions/{}/posts'.format(
            self.api_client.project,
            permalink,
        )
        self.api_client.createpost_in_discussion(permalink, data)

        get_mock.assert_not_called()
        post_mock.assert_called_once_with(expected_url, data)

    def test_notes(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        expected_url = '/{}/tickets/12/notes'.format(self.api_client.project)
        self.api_client.notes(12)

        get_mock.assert_called_once_with(expected_url)
        post_mock.assert_not_called()

    def test_note(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        expected_url = '/{}/tickets/12/notes/94'.format(self.api_client.project)
        self.api_client.note(12, 94)

        get_mock.assert_called_once_with(expected_url)
        post_mock.assert_not_called()

    def test_add_note(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        data = {'some_data': 'some-value'}
        expected_url = '/{}/tickets/12/notes'.format(self.api_client.project)
        self.api_client.add_note(12, data)

        get_mock.assert_not_called()
        post_mock.assert_called_once_with(expected_url, data)

    def test_branches(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        expected_url = '/{}/repo-name/branches'.format(self.api_client.project)
        self.api_client.branches('repo-name')

        get_mock.assert_called_once_with(expected_url)
        post_mock.assert_not_called()

    def test_hooks(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        expected_url = '/{}/repo-name/hooks'.format(self.api_client.project)
        self.api_client.hooks('repo-name')

        get_mock.assert_called_once_with(expected_url)
        post_mock.assert_not_called()

    def test_add_hook(self, get_mock, post_mock):
        get_mock.assert_not_called()
        post_mock.assert_not_called()

        data = {'some_data': 'some-value'}
        expected_url = '/{}/repo-name/hooks'.format(self.api_client.project)
        self.api_client.add_hook('repo-name', data)

        get_mock.assert_not_called()
        post_mock.assert_called_once_with(expected_url, data)
