import errno
import json
import os

from codebase import logger


EXAMPLE_FORMAT = """
{
    "CODEBASE_USERNAME": "foo/bar",
    "CODEBASE_APIKEY": "4ofh783o4hf78o4fh4o"
}
"""


class Settings(object):
    """
    By default settings are expected to be in a file named `.codebase` in your home directory
    """
    SETTINGS_FILE_PATH = '~/.codebase'

    def __init__(self, file_path=None):
        # Initializing the credentials attributes.
        self.username = None
        self.apikey = None

        # Getting the settings path.
        if not file_path or file_path.startswith('~'):
            file_path = file_path or self.SETTINGS_FILE_PATH
            try:
                file_path = os.path.expanduser(file_path)
            except ImportError:
                file_name = os.path.basename(file_path)
                file_path = os.path.join(os.getcwd(), file_name)
                logger.warning(
                    u'Looks like you are running on GoogleAppEngine, which '
                    u'means that "os.path.expanduser" is not supported. '
                    u'Please override the settings logic in '
                    u'`codebase.client.Auth._get_settings` or explicitely '
                    u'pass the required credentials informations.'
                )
                logger.warning(
                    u'The following path will be used in place of the default '
                    u'value: {}'.format(file_path)
                )

        self.file_path = file_path

    def import_settings(self):
        try:
            with open(self.file_path, 'r') as f:
                settings = json.loads(f.read())

            self.username = settings.pop('CODEBASE_USERNAME', None)
            self.apikey = settings.pop('CODEBASE_APIKEY', None)
            assert self.username is not None, '"CODEBASE_USERNAME" is required'
            assert self.apikey is not None, '"CODEBASE_APIKEY" is required'

            for k, v in settings.iteritems():
                setattr(self, k, v)
        except IOError, io_err:
            logger.error(
                u'Settings file "{}" not found. '
                u'Please add your settings in JSON format e.g. {}'.format(
                    self.file_path,
                    EXAMPLE_FORMAT,
                )
            )
            if io_err.errno == errno.EACCES:
                # EACCES = 13, which means "file not accessible" (permission
                # denied).
                logger.error(
                    'The problem could be caused by the name of the file. '
                    'Try to use a non-hidden file name (i.e. a file which '
                    'does not start with a dot).'
                )
