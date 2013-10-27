import base64
import json
import requests


class Auth(object):

	API_ENDPOINT = 'http://api3.codebasehq.com'

	def __init__(self, username, apikey, project, **kwargs):
	    super(CodeBaseAPI, self).__init__(**kwargs)
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

	def statuses(self):
		return self._get('/%s/tickets/statuses' % self.project)

	def priorities(self):
		return self._get('/%s/tickets/priorities' % self.project)

	def categories(self):
		return self._get('/%s/tickets/categories' % self.project)
