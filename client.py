import base64
import requests
import json


class CodeBaseAPI(object):

	API_ENDPOINT = 'http://api3.codebasehq.com/'

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
		return requests.post(self.API_ENDPOINT + url, data=data, headers=self.HEADERS)

	def all_notes(self, ticket_id):
		return self._get('/%s/tickets/%s/notes' % (self.project, ticket_id))

	def get_note(self, ticket_id, note_id):
		return self._get('/%s/tickets/%s/notes/%s' % (self.project, ticket_id, note_id))

	def create_notes(self, ticket_id):
		return self._post('/%s/tickets/%s/notes' % (self.project, ticket_id))