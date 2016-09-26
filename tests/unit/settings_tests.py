from unittest import TestCase
import errno
import json
import os

from mock import call, patch

from codebase.settings import Settings, EXAMPLE_FORMAT
from ..decorators import patch_open


class SettingsTestCase(TestCase):

    def setUp(self):
        super(SettingsTestCase, self).setUp()

        self.home = os.path.expanduser('~')
        self.default_file_path = os.path.join(self.home, '.codebase')

    def test_init_credentials(self):
        settings = Settings()
        self.assertIsNone(settings.username)
        self.assertIsNone(settings.apikey)

    def test_file_path_default(self):
        settings = Settings()
        self.assertEqual(settings.file_path, self.default_file_path)

    def test_file_path_custom_relative_path(self):
        settings = Settings(file_path='./custom.txt')
        self.assertEqual(settings.file_path, './custom.txt')

    def test_file_path_custom_abs_path(self):
        settings = Settings(file_path='/home/user/custom.txt')
        self.assertEqual(settings.file_path, '/home/user/custom.txt')

    def test_file_path_custom_using_expand_user(self):
        settings = Settings(file_path='~/custom.txt')
        self.assertEqual(
            settings.file_path,
            os.path.join(self.home, 'custom.txt')
        )

    @patch('codebase.settings.logger')
    @patch('codebase.settings.os.path.expanduser')
    def test_file_path_default_no_expanduser(self, expanduser_fake, logger_mock):
        # If expanduser is not available (Google AppEngine), the settings file
        # path is set to the current working directory.
        expanduser_fake.side_effect = ImportError
        settings = Settings()
        self.assertEqual(
            settings.file_path,
            os.path.join(os.getcwd(), '.codebase')
        )
        self.assertNotEqual(
            settings.file_path,
            self.default_file_path
        )
        self.assertEqual(logger_mock.warning.call_count, 2)

    @patch('codebase.settings.logger')
    @patch('codebase.settings.os.path.expanduser')
    def test_file_path_custom_no_expanduser(
        self, expanduser_fake, logger_mock
    ):
        # If expanduser is not available (Google AppEngine), the settings file
        # path is set to the current working directory.
        expanduser_fake.side_effect = ImportError
        settings = Settings(file_path='~/.custom.txt')
        self.assertEqual(
            settings.file_path,
            os.path.join(os.getcwd(), '.custom.txt')
        )
        self.assertNotEqual(
            settings.file_path,
            os.path.join(self.home, '.custom.txt')
        )
        self.assertEqual(logger_mock.warning.call_count, 2)

    @patch_open(
        json.dumps({'CODEBASE_USERNAME': 'foo', 'CODEBASE_APIKEY': 'bar'})
    )
    def test_import_settings(self, open_mock):
        settings = Settings()
        self.assertIsNone(settings.username)
        self.assertIsNone(settings.apikey)

        settings.import_settings()

        self.assertEqual(settings.username, 'foo')
        self.assertEqual(settings.apikey, 'bar')
        open_mock.assert_called_with(self.default_file_path, 'r')

    @patch_open(json.dumps(
        {'CODEBASE_USERNAME': 'foo', 'CODEBASE_APIKEY': 'bar', 'other': 'attr'}
    ))
    def test_import_settings_additional_attribute(self, open_mock):
        settings = Settings()
        self.assertIsNone(settings.username)
        self.assertIsNone(settings.apikey)
        self.assertFalse(hasattr(settings, 'other'))

        settings.import_settings()

        self.assertEqual(settings.username, 'foo')
        self.assertEqual(settings.apikey, 'bar')
        self.assertEqual(settings.other, 'attr')
        open_mock.assert_called_with(self.default_file_path, 'r')

    @patch_open('this is not a valid json data')
    def test_import_settings_invalid_json(self, open_mock):
        settings = Settings()
        self.assertIsNone(settings.username)
        self.assertIsNone(settings.apikey)

        with self.assertRaises(ValueError) as err:
            settings.import_settings()

        self.assertEqual(
            err.exception.message,
            'No JSON object could be decoded'
        )
        self.assertIsNone(settings.username)
        self.assertIsNone(settings.apikey)
        open_mock.assert_called_with(self.default_file_path, 'r')

    def test_import_settings_missing_required_attributes(self):
        settings = Settings()

        # CODEBASE_USERNAME is required.
        no_username = json.dumps({'CODEBASE_APIKEY': 'bar'})
        with patch_open(no_username) as open_mock:
            with self.assertRaises(AssertionError) as err:
                settings.import_settings()

        self.assertEqual(
            err.exception.message,
            '"CODEBASE_USERNAME" is required'
        )
        open_mock.assert_called_with(self.default_file_path, 'r')

        # CODEBASE_APIKEY is required.
        no_api_key = json.dumps({'CODEBASE_USERNAME': 'bar'})
        with patch_open(no_api_key) as open_mock:
            with self.assertRaises(AssertionError) as err:
                settings.import_settings()

        self.assertEqual(
            err.exception.message,
            '"CODEBASE_APIKEY" is required'
        )
        open_mock.assert_called_with(self.default_file_path, 'r')

        # None of the required fields is in the json file.
        with patch_open('{}') as open_mock:
            with self.assertRaises(AssertionError) as err:
                settings.import_settings()

        self.assertEqual(
            err.exception.message,
            '"CODEBASE_USERNAME" is required'
        )
        open_mock.assert_called_with(self.default_file_path, 'r')

    @patch('codebase.settings.logger')
    @patch_open(
        json.dumps({'CODEBASE_USERNAME': 'foo', 'CODEBASE_APIKEY': 'bar'}),
    )
    def test_import_settings_io_error(self, open_mock, logger_mock):
        open_mock.side_effect = IOError

        settings = Settings()
        self.assertIsNone(settings.username)
        self.assertIsNone(settings.apikey)

        settings.import_settings()

        self.assertIsNone(settings.username)
        self.assertIsNone(settings.apikey)
        open_mock.assert_called_with(self.default_file_path, 'r')
        logger_mock.error.assert_called_once_with(
            u'Settings file "{}" not found. '
            u'Please add your settings in JSON format e.g. {}'.format(
                settings.file_path,
                EXAMPLE_FORMAT,
            )
        )

    @patch('codebase.settings.logger')
    @patch_open(
        json.dumps({'CODEBASE_USERNAME': 'foo', 'CODEBASE_APIKEY': 'bar'}),
    )
    def test_import_settings_io_error_no_permission(self, open_mock, logger_mock):
        err = IOError()
        err.errno = errno.EACCES
        open_mock.side_effect = err

        settings = Settings()
        self.assertIsNone(settings.username)
        self.assertIsNone(settings.apikey)

        settings.import_settings()

        expected_calls = [
            call(
                u'Settings file "{}" not found. '
                u'Please add your settings in JSON format e.g. {}'.format(
                    settings.file_path,
                    EXAMPLE_FORMAT,
                )
            ),
            call(
                'The problem could be caused by the name of the file. '
                'Try to use a non-hidden file name (i.e. a file which '
                'does not start with a dot).'
            ),
        ]

        self.assertIsNone(settings.username)
        self.assertIsNone(settings.apikey)
        open_mock.assert_called_with(self.default_file_path, 'r')
        logger_mock.error.assert_has_calls(expected_calls)
