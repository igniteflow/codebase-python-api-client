from unittest import TestCase

from codebase.client import CodeBaseAPI


class CodebaseAPITest(TestCase):
    PROJECT = 'foo'

    def setUp(self):
        self.codebase = CodeBaseAPI(project=self.PROJECT)

    def test_statuses(self):
        self.assertIsNotNone(self.codebase.statuses())

    def test_priorities(self):
        self.assertIsNotNone(self.codebase.priorities())

    def test_categories(self):
        self.assertIsNotNone(self.codebase.categories())

    def test_milestones(self):
        self.assertIsNotNone(self.codebase.milestones())

    def test_search(self):
        self.assertIsNotNone(self.codebase.search('one'))
