Codebase API Python Client
==========================

An unofficial CodeBase Python API client.  Example usage:

	codebase = CodeBaseAPI(username=CODEBASE_USERNAME, apikey=CODEBASE_APIKEY, project=project)
	notes = codebase.notes(ticket_id=1)

Data is provided and returned as a Python dictionaries.

CLI
---

There a simple command-line interface to explore the API.  For example, to view all catagories and see the response in the terminal just enter:

	./cli.py [project] categories

Or search:

	./cli.py [project] search [search term]

The CLI can call any function in the CodeBaseAPI class using the syntax:

	./cli.py [project] [function name] *[args]


[API Documentation](http://support.codebasehq.com/kb)
