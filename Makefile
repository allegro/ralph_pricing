install:
	pip install -e .

quicktest:
	DJANGO_SETTINGS_MODULE=ralph_scrooge.settings-test-scrooge scrooge test ralph_scrooge

test-with-coveralls:
	DJANGO_SETTINGS_MODULE=ralph_scrooge.settings-test-scrooge coverage run '$(VIRTUAL_ENV)/bin/scrooge' test ralph_scrooge

coverage:
	make test-with-coveralls
	coverage report

flake:
	flake8 --exclude="migrations" --statistics src/ralph_scrooge

runserver:
	scrooge runserver

install_ui:
	npm install
	./node_modules/.bin/gulp
