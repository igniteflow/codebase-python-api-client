Codebase API Python Client
==========================

A Python client providing read/write access to [Codebase API](http://support.codebasehq.com/kb).  Example usage:

	codebase = CodeBaseAPI(username=CODEBASE_USERNAME, apikey=CODEBASE_APIKEY, project=project)

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


CLI
---

There a simple command-line interface to explore the API.  For example, to view all catagories and see the response in the terminal just enter:

	./cli.py [project] categories

Or search:

	./cli.py [project] search [search term]

The CLI can call any function in the CodeBaseAPI class using the syntax:

	./cli.py [project] [function name] *[args]



