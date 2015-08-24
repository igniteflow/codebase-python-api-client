Codebase API Python Client
==========================

A Python client providing read/write access to the [Codebase API](http://support.codebasehq.com/kb) with a small, but powerful, CLI.

Install
-------

    pip install git+git://github.com/igniteflow/codebase-python-api-client

CLI
---
* After pip install the `codebase` command is availably globally

To use the command-line interface, create a file called .codebase in your home directory and add your Codebase username and apikey (found in your Codebase settings page) in the following JSON format:

    {
        "CODEBASE_USERNAME": "foo/bar",
        "CODEBASE_APIKEY": "4ofh783o4hf78o4fh4o"
    }

You can now explore the API.  To see the available methods:

    codebase

To view all categories for a project and see the response in the terminal:

    codebase [project] categories

Or search:

    codebase [project] search [search term]

The CLI can call any function in the CodeBaseAPI class using the syntax:

    codebase [project] [function name] *[args]


Use the client in your code
---------------------------

    from codebase.client import CodeBaseAPI

    codebase = CodeBaseAPI(username='walter-white', apikey='84gf6479gf674gf', project='MyProject')

	# get all notes for a ticket
	notes = codebase.notes(ticket_id=1) # notes returned as a Python dict

	# update the status of a ticket (see http://support.codebasehq.com/kb/tickets-and-milestones/updating-tickets)
	note_data = {
        'ticket_note': {
            u'content': u'This is the note comment',
            u'changes': {
                u'status_id': u'1631923',
            },
        },
    }
    codebase.add_note(ticket_id=1, data=note_data)
