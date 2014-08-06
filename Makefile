quicktest:
	DJANGO_SETTINGS_PROFILE=test-pricing ralph test ralph_scrooge

test-with-coveralls:
	DJANGO_SETTINGS_PROFILE=test-pricing coverage run --source=ralph_scrooge --omit='*migrations*,*tests*,*__init__*' '$(VIRTUAL_ENV)/bin/ralph' test ralph_scrooge

coverage:
	make test-with-coveralls
	coverage html
	coverage report

flake:
	flake8 --exclude="migrations" --statistics src/ralph_scrooge

runserver:
	ralph runserver
