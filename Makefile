nosetests := nosetests \
	--no-byte-compile \
	--with-coverage \
	--cover-erase \
	--cover-package=codebase \
	--cover-branches \
	--cover-inclusive

runtests-install:
	@clear
	@echo Preflight tasks...
	@pip install -U pip >> /dev/null
	@pip install -r tests/requirements.txt >> /dev/null
	@find ./ -name "*.pyc" -delete >> /dev/null

	@echo Running tests:
	@$(nosetests) --where=tests/unit $(specs)

runtests:
	@clear
	@echo Running tests:
	@$(nosetests) --where=tests/unit $(specs)

runtests-all:
	@clear
	@echo Running tests:
	@$(nosetests) $(specs)
