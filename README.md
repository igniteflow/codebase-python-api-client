Codebase API Python Client
==========================

A Python client providing read/write access to the [Codebase API](http://support.codebasehq.com/kb).  See client.py for the full list of available methods.

Install
-------

    pip install -U git+git://github.com/igniteflow/codebase-python-api-client

Use
---

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
    
Debugging
---------

By default, data is given and returned as Python dicts.  To get the raw Requests Response object, just set CodeBaseAPI.DEBUG to True.

CLI
---

There a simple command-line interface to explore the API.  For example, to view all catagories and see the response in the terminal just enter:

	./cli.py [project] categories

Or search:

	./cli.py [project] search [search term]

The CLI can call any function in the CodeBaseAPI class using the syntax:

	./cli.py [project] [function name] *[args]
