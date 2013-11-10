import unittest

from client import CodeBaseAPI


class CodebaseAPITest(unittest.TestCase):

    PROJECT = 'foo'

    def setUp(self):
        self.codebase = CodeBaseAPI(
            project=self.PROJECT,
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
