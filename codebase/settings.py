import json
from os.path import expanduser


EXAMPLE_FORMAT = """
{
    "CODEBASE_USERNAME": "foo/bar",
    "CODEBASE_APIKEY": "4ofh783o4hf78o4fh4o"
}
"""


class Settings(object):
    SETTINGS_FILE_PATH = expanduser("~") + '/.codebase'

    def get_path(self):
        home = expanduser("~")
        return home + '.codebase'

    def __init__(self):
        try:
            with open(self.SETTINGS_FILE_PATH) as f:
                for k, v in json.loads(f.read()).iteritems():
                    setattr(self, k, v)
        except IOError:
            print('Settings file "~/.codebase" not found.  Please add your settings in JSON format e.g. %s'
                  % EXAMPLE_FORMAT)
