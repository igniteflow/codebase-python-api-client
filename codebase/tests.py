import unittest

from client import CodeBaseAPI
from settings import CODEBASE_USERNAME, CODEBASE_APIKEY, PROJECT


class CodebaseAPITest(unittest.TestCase):
	 
	def setUp(self):
		self.codebase = CodeBaseAPI(
			username=CODEBASE_USERNAME,
			apikey=CODEBASE_APIKEY,
			project=PROJECT,
			debug=True
		)

	def test_statuses(self):
		self.assertEqual(self.codebase.statuses().status_code, 200)

	def test_priorities(self):
		self.assertEqual(self.codebase.priorities().status_code, 200)

	def test_categories(self):
		self.assertEqual(self.codebase.categories().status_code, 200)

	def test_milestones(self):
		self.assertEqual(self.codebase.milestones().status_code, 200)

	def test_search(self):
		self.assertEqual(self.codebase.search('one').status_code, 200)

if __name__ == '__main__':
    unittest.main()
