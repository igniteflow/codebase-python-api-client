import base64
import json
import requests


class Auth(object):

	API_ENDPOINT = 'http://api3.codebasehq.com'

	def __init__(self, username, apikey, project, **kwargs):
	    super(Auth, self).__init__(**kwargs)
	    self.username = username
	    self.apikey = apikey
	    self.project = project
	    self.HEADERS = {
			"Content-type": "application/json",
		    "Accept": "application/json",
			"Authorization": base64.encodestring("%s:%s" % (self.username, self.apikey))\
				.replace('\n', '')
		}
	
	def _get(self, url): 
		response = requests.get(self.API_ENDPOINT + url, headers=self.HEADERS)
		return json.loads(response.content)

	def _post(self, url, data):
		response = requests.post(self.API_ENDPOINT + url, data=json.dumps(data), headers=self.HEADERS)
		return json.loads(response.content)


class CodeBaseAPI(Auth):

	def statuses(self):
		return self._get('/%s/tickets/statuses' % self.project)

	def priorities(self):
		return self._get('/%s/tickets/priorities' % self.project)

	def categories(self):
		return self._get('/%s/tickets/categories' % self.project)

	def milestones(self):
		return self._get('/%s/tickets/milestones' % self.project)

	def search(self, term):
		return self._get('/%s/tickets?query=%s' % (self.project, term))

	def watchers(self, ticket_id):
		return self._get('/%s/tickets/%s/watchers' % (self.project, ticket_id))

	def project_groups(self):
		return self._get('/project_groups')

	def get_project_users(self):
		return self._get('/%s/assignments' % self.project)

	def set_project_users(self, data):
		return self._post('/%s/assignments' % self.project, data)

	def activity(self):
		return self._get('/activity')

	def project_activity(self):
		return self._get('/%s/activity' % self.project)

	def users(self):
		return self._get('/users')

	def roles(self):
		return self._get('/roles')

	def discussions(self):
		return self._get('/%s/discussions' % self.project)

	def discussion_categories(self):
		return self._get('/%s/discussions/categories' % self.project)

	def create_discussion(self, data):
		return self._post('/%s/discussions' % self.project, data)

	def posts_in_discussion(self, discussion_permalink):
		return self._get('/%s/discussions/%s/posts' % (self.project, discussion_permalink))

	def create_post_in_discussion(self, discussion_permalink, data):
		return self._post('/%s/discussions/%s/posts' % (self.project, discussion_permalink), data)

	def all_notes(self, ticket_id):
		return self._get('/%s/tickets/%s/notes' % (self.project, ticket_id))

	def get_note(self, ticket_id, note_id):
		return self._get('/%s/tickets/%s/notes/%s' % (self.project, ticket_id, note_id))

	def create_note(self, ticket_id, data):
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
		return self._post('/%s/tickets/%s/notes' % (self.project, ticket_id), data)


