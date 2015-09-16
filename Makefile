install:
	pip install -e .

quicktest:
	DJANGO_SETTINGS_MODULE=ralph_scrooge.settings.test scrooge test ralph_scrooge

test-with-coveralls:
	DJANGO_SETTINGS_MODULE=ralph_scrooge.settings.test coverage run --source=ralph_scrooge --omit='*migrations*,*tests*,*__init__*' '$(VIRTUAL_ENV)/bin/scrooge' test ralph_scrooge

coverage:
	make test-with-coveralls
	coverage html
	coverage report

flake:
	flake8 --exclude="__migrations,settings" --statistics src/ralph_scrooge

runserver:
	scrooge runserver
