import base64
import os
import requests
import sys


CODEBASE_USERNAME=os.environ['CODEBASE_USERNAME']
CODEBASE_APIKEY=os.environ['CODEBASE_APIKEY']


class CodeBaseAPI(object):

	HEADERS = {
		"Content-type": "application/xml",
	    "Accept": "application/xml",
		"Authorization": base64.encodestring("%s:%s" % (CODEBASE_USERNAME, CODEBASE_APIKEY)).replace('\n', '')
	}
	API = 'http://api3.codebasehq.com/'

	def __init__(self, username, apikey, **kwargs):
	    super(CodeBaseAPI, self).__init__(**kwargs)
	    self.username = username
	    self.apikey = apikey
	
	def get(self, url): 
		return requests.get(self.API + url, headers=self.HEADERS)

	def post(self, url, data):
		return requests.post(self.API + url, data=data, headers=self.HEADERS)


class Note(object):

	def __init__(self, project, *args, **kwargs):
	    super(Note, self).__init__(*args, **kwargs)
	    self.project = project

	def all_for_ticket(self, ticket_id):
		return '/%s/tickets/%s/notes' % (self.project, ticket_id)


	def get(self, ticket_id, note_id):
		return '/%s/tickets/%s/notes/%s' % (self.project, ticket_id, note_id)

	def create(self, ticket_id):
		return '/%s/tickets/%s/notes' % (self.project, ticket_id)


# example usage
PROJECT = 'foo'
TICKET_NUMBER = 123

codebase = CodeBaseAPI(username=CODEBASE_USERNAME, apikey=CODEBASE_APIKEY)
response = codebase.get(Note(project=PROJECT).all_for_ticket(ticket_id=TICKET_ID))
